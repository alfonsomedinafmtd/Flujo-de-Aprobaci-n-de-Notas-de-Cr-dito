from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import (
    CreditNoteAction,
    CreditNoteStatus,
    Currency,
    EmployeeStatus,
    Seniority,
    UserRole,
)


def utc_now() -> datetime:
    """Return a naive datetime whose value is always UTC for DB portability."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


position_functions = Table(
    "position_functions",
    Base.metadata,
    Column("position_id", ForeignKey("positions.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "business_function_id",
        ForeignKey("business_functions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    positions: Mapped[list[Position]] = relationship(back_populates="department")
    credit_notes: Mapped[list[CreditNote]] = relationship(back_populates="requesting_department")


class BusinessFunction(Base):
    __tablename__ = "business_functions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(Text)

    positions: Mapped[list[Position]] = relationship(
        secondary=position_functions,
        back_populates="functions",
    )


class Position(Base):
    __tablename__ = "positions"
    __table_args__ = (UniqueConstraint("department_id", "title"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    title: Mapped[str] = mapped_column(String(100))
    seniority: Mapped[Seniority] = mapped_column(
        SqlEnum(Seniority, name="position_seniority", native_enum=False, create_constraint=True),
    )
    description: Mapped[str | None] = mapped_column(Text)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department: Mapped[Department] = relationship(back_populates="positions")
    functions: Mapped[list[BusinessFunction]] = relationship(
        secondary=position_functions,
        back_populates="positions",
    )
    employees: Mapped[list[Employee]] = relationship(back_populates="position")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    position_id: Mapped[int] = mapped_column(ForeignKey("positions.id"), index=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    country: Mapped[str] = mapped_column(String(80))
    hire_date: Mapped[date] = mapped_column(Date)
    internal_email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    status: Mapped[EmployeeStatus] = mapped_column(
        SqlEnum(EmployeeStatus, name="employee_status", native_enum=False, create_constraint=True),
        default=EmployeeStatus.ACTIVE,
    )

    position: Mapped[Position] = relationship(back_populates="employees")
    user_account: Mapped[UserAccount | None] = relationship(back_populates="employee", uselist=False)


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"), unique=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, name="user_role", native_enum=False, create_constraint=True),
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    employee: Mapped[Employee] = relationship(back_populates="user_account")
    sessions: Mapped[list[AuthSession]] = relationship(back_populates="user")
    created_credit_notes: Mapped[list[CreditNote]] = relationship(back_populates="creator")
    credit_note_events: Mapped[list[CreditNoteEvent]] = relationship(back_populates="actor")


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_accounts.id"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    csrf_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    user: Mapped[UserAccount] = relationship(back_populates="sessions")


class Store(Base):
    __tablename__ = "stores"
    __table_args__ = (UniqueConstraint("name", "country"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    country: Mapped[str] = mapped_column(String(80))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    credit_notes: Mapped[list[CreditNote]] = relationship(back_populates="store")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(140), unique=True)
    industry: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    credit_notes: Mapped[list[CreditNote]] = relationship(back_populates="company")


class CreditNote(Base):
    __tablename__ = "credit_notes"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        Index("ix_credit_notes_department_status", "requesting_department_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[Currency] = mapped_column(
        SqlEnum(Currency, name="credit_note_currency", native_enum=False, create_constraint=True),
    )
    reason: Mapped[str] = mapped_column(Text)
    requesting_department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"), index=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("user_accounts.id"), index=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    status: Mapped[CreditNoteStatus] = mapped_column(
        SqlEnum(CreditNoteStatus, name="credit_note_status", native_enum=False, create_constraint=True),
        default=CreditNoteStatus.PENDING,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    requesting_department: Mapped[Department] = relationship(back_populates="credit_notes")
    creator: Mapped[UserAccount] = relationship(back_populates="created_credit_notes")
    store: Mapped[Store] = relationship(back_populates="credit_notes")
    company: Mapped[Company] = relationship(back_populates="credit_notes")
    events: Mapped[list[CreditNoteEvent]] = relationship(
        back_populates="credit_note",
        order_by="CreditNoteEvent.occurred_at",
    )


class CreditNoteEvent(Base):
    __tablename__ = "credit_note_events"
    __table_args__ = (Index("ix_credit_note_events_note_time", "credit_note_id", "occurred_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    credit_note_id: Mapped[int] = mapped_column(ForeignKey("credit_notes.id"), index=True)
    actor_user_id: Mapped[int] = mapped_column(ForeignKey("user_accounts.id"), index=True)
    action: Mapped[CreditNoteAction] = mapped_column(
        SqlEnum(
            CreditNoteAction,
            name="credit_note_event_action",
            native_enum=False,
            create_constraint=True,
        ),
    )
    previous_status: Mapped[CreditNoteStatus | None] = mapped_column(
        SqlEnum(
            CreditNoteStatus,
            name="credit_note_event_previous_status",
            native_enum=False,
            create_constraint=True,
        ),
    )
    new_status: Mapped[CreditNoteStatus] = mapped_column(
        SqlEnum(
            CreditNoteStatus,
            name="credit_note_event_new_status",
            native_enum=False,
            create_constraint=True,
        ),
    )
    comment: Mapped[str | None] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    credit_note: Mapped[CreditNote] = relationship(back_populates="events")
    actor: Mapped[UserAccount] = relationship(back_populates="credit_note_events")
