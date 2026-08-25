from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from app.enums import CreditNoteAction, CreditNoteStatus, Currency, EmployeeStatus, Seniority, UserRole


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=3, max_length=80)
    password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class CurrentUserRead(BaseModel):
    id: int
    username: str
    role: UserRole
    employee_id: int
    full_name: str
    internal_email: str
    department_id: int
    department_name: str


class LoginResponse(BaseModel):
    user: CurrentUserRead
    csrf_token: str


class CsrfResponse(BaseModel):
    csrf_token: str


class DepartmentRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class BusinessFunctionRead(BaseModel):
    id: int
    code: str
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class PositionRead(BaseModel):
    id: int
    title: str
    seniority: Seniority
    department: DepartmentRead
    functions: list[BusinessFunctionRead]


class EmployeeDirectoryRead(BaseModel):
    id: int
    full_name: str
    position_title: str
    seniority: Seniority
    department_name: str
    status: EmployeeStatus


class EmployeeDetailRead(EmployeeDirectoryRead):
    country: str
    hire_date: date
    internal_email: str
    username: str | None
    portal_role: UserRole | None


class CatalogItemRead(BaseModel):
    id: int
    name: str


class CreditNoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: Currency
    reason: str = Field(min_length=5, max_length=1000)
    store_id: int = Field(gt=0)
    company_id: int = Field(gt=0)

    @field_validator("reason", mode="before")
    @classmethod
    def strip_reason(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class CreditNoteDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    expected_version: int = Field(ge=1)
    comment: str | None = Field(default=None, max_length=1000)

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class CreditNoteEventRead(BaseModel):
    id: int
    action: CreditNoteAction
    previous_status: CreditNoteStatus | None
    new_status: CreditNoteStatus
    comment: str | None
    actor_id: int
    actor_username: str
    actor_full_name: str
    actor_role: UserRole
    occurred_at: datetime


class CreditNoteRead(BaseModel):
    id: int
    amount: Decimal
    currency: Currency
    reason: str
    status: CreditNoteStatus
    version: int
    requesting_department: DepartmentRead
    creator_id: int
    creator_username: str
    creator_full_name: str
    creator_internal_email: str
    creator_role: UserRole
    requester_position_title: str
    store: CatalogItemRead
    company: CatalogItemRead
    created_at: datetime
    updated_at: datetime
    events: list[CreditNoteEventRead] = Field(default_factory=list)


class CreditNoteListRead(BaseModel):
    items: list[CreditNoteRead]
    total: int
    limit: int
    offset: int


class CreditNoteSummaryRead(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int


class CreditNoteCatalogRead(BaseModel):
    stores: list[CatalogItemRead]
    companies: list[CatalogItemRead]


class CreditNoteAnalyticsCountsRead(BaseModel):
    total: int
    pending: int
    approved: int
    rejected: int


class CreditNoteAnalyticsSummaryRead(CreditNoteAnalyticsCountsRead):
    approval_rate: float
    rejection_rate: float
    average_resolution_hours: float | None


class CreditNoteAnalyticsAmountRead(BaseModel):
    currency: Currency
    total_amount: Decimal
    average_amount: Decimal


class CreditNoteAnalyticsGroupRead(CreditNoteAnalyticsCountsRead):
    key: str
    label: str
    amounts: list[CreditNoteAnalyticsAmountRead]


class CreditNoteAnalyticsRequesterRead(CreditNoteAnalyticsCountsRead):
    user_id: int
    username: str
    full_name: str
    department_name: str
    position_title: str
    amounts: list[CreditNoteAnalyticsAmountRead]


class CreditNoteAnalyticsTrendRead(CreditNoteAnalyticsCountsRead):
    period: str


class CreditNoteAnalyticsPendingRead(BaseModel):
    id: int
    requester_full_name: str
    department_name: str
    position_title: str
    amount: Decimal
    currency: Currency
    created_at: datetime
    age_days: int


class CreditNoteAnalyticsRead(BaseModel):
    summary: CreditNoteAnalyticsSummaryRead
    amounts: list[CreditNoteAnalyticsAmountRead]
    departments: list[DepartmentRead]
    by_department: list[CreditNoteAnalyticsGroupRead]
    by_position: list[CreditNoteAnalyticsGroupRead]
    by_requester: list[CreditNoteAnalyticsRequesterRead]
    trend: list[CreditNoteAnalyticsTrendRead]
    oldest_pending: list[CreditNoteAnalyticsPendingRead]
