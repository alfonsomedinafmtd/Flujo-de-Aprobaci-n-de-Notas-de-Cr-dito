from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    COLLABORATOR = "COLLABORATOR"


class EmployeeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Seniority(str, Enum):
    ASSISTANT = "ASSISTANT"
    JUNIOR = "JUNIOR"
    SEMI_SENIOR = "SEMI_SENIOR"
    SENIOR = "SENIOR"
    LEAD = "LEAD"


class Currency(str, Enum):
    USD = "USD"
    VES = "VES"


class CreditNoteStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CreditNoteAction(str, Enum):
    CREATED = "CREATED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

