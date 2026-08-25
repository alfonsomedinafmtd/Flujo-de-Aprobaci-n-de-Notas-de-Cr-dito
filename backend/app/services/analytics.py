from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.enums import CreditNoteStatus, Currency, UserRole
from app.models import CreditNote, Department, Employee, UserAccount, utc_now
from app.schemas import (
    CreditNoteAnalyticsAmountRead,
    CreditNoteAnalyticsGroupRead,
    CreditNoteAnalyticsPendingRead,
    CreditNoteAnalyticsRead,
    CreditNoteAnalyticsRequesterRead,
    CreditNoteAnalyticsSummaryRead,
    CreditNoteAnalyticsTrendRead,
    DepartmentRead,
)


MONEY_QUANTUM = Decimal("0.01")


@dataclass
class _Bucket:
    total: int = 0
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    amounts: dict[Currency, Decimal] = field(
        default_factory=lambda: defaultdict(lambda: Decimal("0"))
    )
    amount_counts: dict[Currency, int] = field(default_factory=lambda: defaultdict(int))

    def add(self, note: CreditNote) -> None:
        self.total += 1
        if note.status is CreditNoteStatus.PENDING:
            self.pending += 1
        elif note.status is CreditNoteStatus.APPROVED:
            self.approved += 1
        else:
            self.rejected += 1
        self.amounts[note.currency] += note.amount
        self.amount_counts[note.currency] += 1


def _amount_rows(bucket: _Bucket) -> list[CreditNoteAnalyticsAmountRead]:
    return [
        CreditNoteAnalyticsAmountRead(
            currency=currency,
            total_amount=total.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP),
            average_amount=(total / bucket.amount_counts[currency]).quantize(
                MONEY_QUANTUM,
                rounding=ROUND_HALF_UP,
            ),
        )
        for currency, total in sorted(bucket.amounts.items(), key=lambda item: item[0].value)
    ]


def _group_row(key: str, label: str, bucket: _Bucket) -> CreditNoteAnalyticsGroupRead:
    return CreditNoteAnalyticsGroupRead(
        key=key,
        label=label,
        total=bucket.total,
        pending=bucket.pending,
        approved=bucket.approved,
        rejected=bucket.rejected,
        amounts=_amount_rows(bucket),
    )


def get_credit_note_analytics(
    db: Session,
    user: UserAccount,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    department_id: int | None = None,
    status_filter: CreditNoteStatus | None = None,
) -> CreditNoteAnalyticsRead:
    if user.role is not UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso insuficiente")
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="La fecha inicial no puede ser posterior a la fecha final",
        )

    conditions = []
    if date_from is not None:
        conditions.append(CreditNote.created_at >= datetime.combine(date_from, time.min))
    if date_to is not None:
        conditions.append(
            CreditNote.created_at < datetime.combine(date_to + timedelta(days=1), time.min)
        )
    if department_id is not None:
        conditions.append(CreditNote.requesting_department_id == department_id)
    if status_filter is not None:
        conditions.append(CreditNote.status == status_filter)

    statement = (
        select(CreditNote)
        .where(*conditions)
        .options(
            joinedload(CreditNote.requesting_department),
            joinedload(CreditNote.creator)
            .joinedload(UserAccount.employee)
            .joinedload(Employee.position),
        )
        .order_by(CreditNote.created_at, CreditNote.id)
    )
    notes = list(db.scalars(statement).unique())
    departments = list(
        db.scalars(
            select(Department).where(Department.active.is_(True)).order_by(Department.name)
        )
    )

    summary = _Bucket()
    department_buckets: dict[tuple[int, str], _Bucket] = defaultdict(_Bucket)
    position_buckets: dict[str, _Bucket] = defaultdict(_Bucket)
    requester_buckets: dict[int, _Bucket] = defaultdict(_Bucket)
    requester_metadata: dict[int, tuple[str, str, str, str]] = {}
    trend_buckets: dict[str, _Bucket] = defaultdict(_Bucket)
    resolution_hours: list[float] = []

    for note in notes:
        summary.add(note)
        department_buckets[(note.requesting_department.id, note.requesting_department.name)].add(note)
        position_buckets[note.requester_position_title].add(note)
        requester_buckets[note.creator.id].add(note)
        requester_metadata[note.creator.id] = (
            note.creator.username,
            f"{note.creator.employee.first_name} {note.creator.employee.last_name}",
            note.requesting_department.name,
            note.requester_position_title,
        )
        trend_buckets[note.created_at.strftime("%Y-%m")].add(note)
        if note.status is not CreditNoteStatus.PENDING:
            resolution_hours.append((note.updated_at - note.created_at).total_seconds() / 3600)

    resolved = summary.approved + summary.rejected
    average_resolution = (
        round(sum(resolution_hours) / len(resolution_hours), 1) if resolution_hours else None
    )
    summary_read = CreditNoteAnalyticsSummaryRead(
        total=summary.total,
        pending=summary.pending,
        approved=summary.approved,
        rejected=summary.rejected,
        approval_rate=round(summary.approved * 100 / resolved, 1) if resolved else 0,
        rejection_rate=round(summary.rejected * 100 / resolved, 1) if resolved else 0,
        average_resolution_hours=average_resolution,
    )

    by_department = [
        _group_row(str(department_id_value), department_name, bucket)
        for (department_id_value, department_name), bucket in sorted(
            department_buckets.items(), key=lambda item: (-item[1].total, item[0][1])
        )
    ]
    by_position = [
        _group_row(position_title, position_title, bucket)
        for position_title, bucket in sorted(
            position_buckets.items(), key=lambda item: (-item[1].total, item[0])
        )
    ]
    by_requester = []
    for user_id, bucket in sorted(
        requester_buckets.items(), key=lambda item: (-item[1].total, requester_metadata[item[0]][1])
    ):
        username, full_name, department_name, position_title = requester_metadata[user_id]
        by_requester.append(
            CreditNoteAnalyticsRequesterRead(
                user_id=user_id,
                username=username,
                full_name=full_name,
                department_name=department_name,
                position_title=position_title,
                total=bucket.total,
                pending=bucket.pending,
                approved=bucket.approved,
                rejected=bucket.rejected,
                amounts=_amount_rows(bucket),
            )
        )

    trend = [
        CreditNoteAnalyticsTrendRead(
            period=period,
            total=bucket.total,
            pending=bucket.pending,
            approved=bucket.approved,
            rejected=bucket.rejected,
        )
        for period, bucket in sorted(trend_buckets.items())
    ]

    today = utc_now().date()
    oldest_pending = [
        CreditNoteAnalyticsPendingRead(
            id=note.id,
            requester_full_name=f"{note.creator.employee.first_name} {note.creator.employee.last_name}",
            department_name=note.requesting_department.name,
            position_title=note.requester_position_title,
            amount=note.amount,
            currency=note.currency,
            created_at=note.created_at,
            age_days=max((today - note.created_at.date()).days, 0),
        )
        for note in sorted(
            (item for item in notes if item.status is CreditNoteStatus.PENDING),
            key=lambda item: (item.created_at, item.id),
        )[:8]
    ]

    return CreditNoteAnalyticsRead(
        summary=summary_read,
        amounts=_amount_rows(summary),
        departments=[DepartmentRead.model_validate(item) for item in departments],
        by_department=by_department,
        by_position=by_position,
        by_requester=by_requester,
        trend=trend,
        oldest_pending=oldest_pending,
    )
