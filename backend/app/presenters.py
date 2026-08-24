from app.models import CreditNote, Employee, Position, UserAccount
from app.schemas import (
    BusinessFunctionRead,
    CatalogItemRead,
    CreditNoteEventRead,
    CreditNoteRead,
    CurrentUserRead,
    DepartmentRead,
    EmployeeDetailRead,
    EmployeeDirectoryRead,
    PositionRead,
)


def present_current_user(user: UserAccount) -> CurrentUserRead:
    employee = user.employee
    department = employee.position.department
    return CurrentUserRead(
        id=user.id,
        username=user.username,
        role=user.role,
        employee_id=employee.id,
        full_name=f"{employee.first_name} {employee.last_name}",
        internal_email=employee.internal_email,
        department_id=department.id,
        department_name=department.name,
    )


def present_employee_directory(employee: Employee) -> EmployeeDirectoryRead:
    return EmployeeDirectoryRead(
        id=employee.id,
        full_name=f"{employee.first_name} {employee.last_name}",
        position_title=employee.position.title,
        seniority=employee.position.seniority,
        department_name=employee.position.department.name,
        status=employee.status,
    )


def present_employee_detail(employee: Employee) -> EmployeeDetailRead:
    directory = present_employee_directory(employee)
    return EmployeeDetailRead(
        **directory.model_dump(),
        country=employee.country,
        hire_date=employee.hire_date,
        internal_email=employee.internal_email,
    )


def present_position(position: Position) -> PositionRead:
    return PositionRead(
        id=position.id,
        title=position.title,
        seniority=position.seniority,
        department=DepartmentRead.model_validate(position.department),
        functions=[BusinessFunctionRead.model_validate(item) for item in position.functions],
    )


def present_credit_note(note: CreditNote) -> CreditNoteRead:
    return CreditNoteRead(
        id=note.id,
        amount=note.amount,
        currency=note.currency,
        reason=note.reason,
        status=note.status,
        version=note.version,
        requesting_department=DepartmentRead.model_validate(note.requesting_department),
        creator_id=note.creator.id,
        creator_username=note.creator.username,
        store=CatalogItemRead(id=note.store.id, name=note.store.name),
        company=CatalogItemRead(id=note.company.id, name=note.company.name),
        created_at=note.created_at,
        updated_at=note.updated_at,
        events=[
            CreditNoteEventRead(
                id=event.id,
                action=event.action,
                previous_status=event.previous_status,
                new_status=event.new_status,
                comment=event.comment,
                actor_id=event.actor.id,
                actor_username=event.actor.username,
                actor_role=event.actor.role,
                occurred_at=event.occurred_at,
            )
            for event in note.events
        ],
    )

