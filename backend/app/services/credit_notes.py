from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session, joinedload, selectinload

from app.enums import CreditNoteAction, CreditNoteStatus, UserRole
from app.models import (
    Company,
    CreditNote,
    CreditNoteEvent,
    Store,
    UserAccount,
    utc_now,
)
from app.schemas import CreditNoteCreate, CreditNoteDecision


def _note_options():
    return (
        joinedload(CreditNote.requesting_department),
        joinedload(CreditNote.creator),
        joinedload(CreditNote.store),
        joinedload(CreditNote.company),
        selectinload(CreditNote.events).joinedload(CreditNoteEvent.actor),
    )


def _department_id(user: UserAccount) -> int:
    return user.employee.position.department_id


def _scope_conditions(user: UserAccount) -> list:
    if user.role is UserRole.ADMIN:
        return []
    if user.role is UserRole.DEPARTMENT_HEAD:
        return [CreditNote.requesting_department_id == _department_id(user)]
    return [CreditNote.created_by_user_id == user.id]


def list_credit_notes(
    db: Session,
    user: UserAccount,
    *,
    limit: int,
    offset: int,
) -> tuple[list[CreditNote], int]:
    conditions = _scope_conditions(user)
    statement = (
        select(CreditNote)
        .where(*conditions)
        .options(*_note_options())
        .order_by(CreditNote.created_at.desc(), CreditNote.id.desc())
        .limit(limit)
        .offset(offset)
    )
    count_statement = select(func.count(CreditNote.id)).where(*conditions)
    return list(db.scalars(statement).all()), db.scalar(count_statement) or 0


def get_credit_note(db: Session, user: UserAccount, note_id: int) -> CreditNote:
    statement = (
        select(CreditNote)
        .where(CreditNote.id == note_id, *_scope_conditions(user))
        .options(*_note_options())
    )
    note = db.scalar(statement)
    if note is None:
        # A 404 avoids revelar si el identificador existe en otro departamento.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nota de crédito no encontrada")
    return note


def create_credit_note(
    db: Session,
    user: UserAccount,
    payload: CreditNoteCreate,
) -> CreditNote:
    if user.role is not UserRole.COLLABORATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el rol colaborador puede crear solicitudes",
        )

    store = db.get(Store, payload.store_id)
    company = db.get(Company, payload.company_id)
    if store is None or not store.active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Tienda inválida")
    if company is None or not company.active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Compañía inválida")

    now = utc_now()
    note = CreditNote(
        amount=payload.amount,
        currency=payload.currency,
        reason=payload.reason,
        requesting_department_id=_department_id(user),
        created_by_user_id=user.id,
        store_id=payload.store_id,
        company_id=payload.company_id,
        status=CreditNoteStatus.PENDING,
        version=1,
        created_at=now,
        updated_at=now,
    )
    db.add(note)
    db.flush()
    db.add(
        CreditNoteEvent(
            credit_note_id=note.id,
            actor_user_id=user.id,
            action=CreditNoteAction.CREATED,
            previous_status=None,
            new_status=CreditNoteStatus.PENDING,
            comment="Solicitud creada",
            occurred_at=now,
        )
    )
    db.commit()
    return get_credit_note(db, user, note.id)


def decide_credit_note(
    db: Session,
    actor: UserAccount,
    note_id: int,
    payload: CreditNoteDecision,
    *,
    new_status: CreditNoteStatus,
) -> CreditNote:
    if actor.role not in {UserRole.ADMIN, UserRole.DEPARTMENT_HEAD}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol no autorizado para decidir")
    if new_status not in {CreditNoteStatus.APPROVED, CreditNoteStatus.REJECTED}:
        raise ValueError("La decisión debe ser APPROVED o REJECTED")
    if new_status is CreditNoteStatus.REJECTED and not payload.comment:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="El rechazo requiere un comentario",
        )

    note = get_credit_note(db, actor, note_id)
    if note.status is not CreditNoteStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La solicitud ya fue resuelta")
    if note.version != payload.expected_version:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La solicitud cambió; actualiza la vista")
    if note.created_by_user_id == actor.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se permite la autoaprobación")
    if note.creator.role is actor.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El aprobador debe pertenecer a un rol distinto del solicitante",
        )

    now = utc_now()
    result = db.execute(
        update(CreditNote)
        .where(
            CreditNote.id == note.id,
            CreditNote.status == CreditNoteStatus.PENDING,
            CreditNote.version == payload.expected_version,
        )
        .values(
            status=new_status,
            version=CreditNote.version + 1,
            updated_at=now,
        )
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La solicitud fue procesada por otro usuario",
        )

    action = (
        CreditNoteAction.APPROVED
        if new_status is CreditNoteStatus.APPROVED
        else CreditNoteAction.REJECTED
    )
    db.add(
        CreditNoteEvent(
            credit_note_id=note.id,
            actor_user_id=actor.id,
            action=action,
            previous_status=CreditNoteStatus.PENDING,
            new_status=new_status,
            comment=payload.comment,
            occurred_at=now,
        )
    )
    db.commit()
    db.expire_all()
    return get_credit_note(db, actor, note.id)
