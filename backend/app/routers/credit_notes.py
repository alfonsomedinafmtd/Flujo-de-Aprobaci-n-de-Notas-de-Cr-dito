from fastapi import APIRouter, Query, status
from sqlalchemy import select

from app.dependencies import CsrfAuth, CurrentUser, DbSession
from app.enums import CreditNoteStatus
from app.models import Company, Store
from app.presenters import present_credit_note
from app.schemas import (
    CatalogItemRead,
    CreditNoteCatalogRead,
    CreditNoteCreate,
    CreditNoteDecision,
    CreditNoteListRead,
    CreditNoteRead,
)
from app.services.credit_notes import (
    create_credit_note,
    decide_credit_note,
    get_credit_note,
    list_credit_notes,
)


router = APIRouter(prefix="/credit-notes", tags=["credit-notes"])


@router.get("/catalog", response_model=CreditNoteCatalogRead)
def catalog(db: DbSession, _user: CurrentUser) -> CreditNoteCatalogRead:
    stores = db.scalars(select(Store).where(Store.active.is_(True)).order_by(Store.name)).all()
    companies = db.scalars(select(Company).where(Company.active.is_(True)).order_by(Company.name)).all()
    return CreditNoteCatalogRead(
        stores=[CatalogItemRead(id=item.id, name=item.name) for item in stores],
        companies=[CatalogItemRead(id=item.id, name=item.name) for item in companies],
    )


@router.get("", response_model=CreditNoteListRead)
def list_notes(
    db: DbSession,
    user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    note_status: CreditNoteStatus | None = Query(default=None, alias="status"),
) -> CreditNoteListRead:
    notes, total = list_credit_notes(
        db,
        user,
        limit=limit,
        offset=offset,
        status_filter=note_status,
    )
    return CreditNoteListRead(
        items=[present_credit_note(note) for note in notes],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=CreditNoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: CreditNoteCreate, context: CsrfAuth, db: DbSession) -> CreditNoteRead:
    return present_credit_note(create_credit_note(db, context.user, payload))


@router.get("/{note_id}", response_model=CreditNoteRead)
def note_detail(note_id: int, db: DbSession, user: CurrentUser) -> CreditNoteRead:
    return present_credit_note(get_credit_note(db, user, note_id))


@router.post("/{note_id}/approve", response_model=CreditNoteRead)
def approve_note(
    note_id: int,
    payload: CreditNoteDecision,
    context: CsrfAuth,
    db: DbSession,
) -> CreditNoteRead:
    note = decide_credit_note(
        db,
        context.user,
        note_id,
        payload,
        new_status=CreditNoteStatus.APPROVED,
    )
    return present_credit_note(note)


@router.post("/{note_id}/reject", response_model=CreditNoteRead)
def reject_note(
    note_id: int,
    payload: CreditNoteDecision,
    context: CsrfAuth,
    db: DbSession,
) -> CreditNoteRead:
    note = decide_credit_note(
        db,
        context.user,
        note_id,
        payload,
        new_status=CreditNoteStatus.REJECTED,
    )
    return present_credit_note(note)
