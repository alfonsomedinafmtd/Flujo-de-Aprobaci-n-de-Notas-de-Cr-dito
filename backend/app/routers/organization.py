from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.dependencies import CurrentUser, DbSession
from app.enums import EmployeeStatus, UserRole
from app.models import Department, Employee, Position
from app.presenters import (
    present_employee_detail,
    present_employee_directory,
    present_position,
)
from app.schemas import (
    DepartmentRead,
    EmployeeDetailRead,
    EmployeeDirectoryRead,
    PositionRead,
)


router = APIRouter(prefix="/organization", tags=["organization"])


def _own_department_id(user: CurrentUser) -> int:
    return user.employee.position.department_id


def _validate_department_scope(user: CurrentUser, requested_department_id: int | None) -> int | None:
    if user.role is UserRole.ADMIN:
        return requested_department_id
    own_id = _own_department_id(user)
    if requested_department_id is not None and requested_department_id != own_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Departamento fuera de alcance")
    return own_id


@router.get("/departments", response_model=list[DepartmentRead])
def list_departments(db: DbSession, user: CurrentUser) -> list[DepartmentRead]:
    statement = select(Department).where(Department.active.is_(True)).order_by(Department.name)
    if user.role is not UserRole.ADMIN:
        statement = statement.where(Department.id == _own_department_id(user))
    return [DepartmentRead.model_validate(item) for item in db.scalars(statement)]


@router.get("/profile", response_model=EmployeeDetailRead)
def profile(user: CurrentUser) -> EmployeeDetailRead:
    return present_employee_detail(user.employee)


@router.get("/directory", response_model=list[EmployeeDirectoryRead])
def directory(
    db: DbSession,
    user: CurrentUser,
    department_id: int | None = Query(default=None, gt=0),
) -> list[EmployeeDirectoryRead]:
    scoped_department_id = _validate_department_scope(user, department_id)
    statement = (
        select(Employee)
        .join(Employee.position)
        .options(joinedload(Employee.position).joinedload(Position.department))
        .order_by(Employee.last_name, Employee.first_name)
    )
    if scoped_department_id is not None:
        statement = statement.where(Position.department_id == scoped_department_id)
    if user.role is UserRole.COLLABORATOR:
        statement = statement.where(Employee.status == EmployeeStatus.ACTIVE)
    return [present_employee_directory(item) for item in db.scalars(statement)]


@router.get("/employees", response_model=list[EmployeeDetailRead])
def employees(
    db: DbSession,
    user: CurrentUser,
    department_id: int | None = Query(default=None, gt=0),
) -> list[EmployeeDetailRead]:
    if user.role is UserRole.COLLABORATOR:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso insuficiente")
    scoped_department_id = _validate_department_scope(user, department_id)
    statement = (
        select(Employee)
        .join(Employee.position)
        .options(joinedload(Employee.position).joinedload(Position.department))
        .order_by(Employee.last_name, Employee.first_name)
    )
    if scoped_department_id is not None:
        statement = statement.where(Position.department_id == scoped_department_id)
    return [present_employee_detail(item) for item in db.scalars(statement)]


@router.get("/positions", response_model=list[PositionRead])
def positions(
    db: DbSession,
    user: CurrentUser,
    department_id: int | None = Query(default=None, gt=0),
) -> list[PositionRead]:
    scoped_department_id = _validate_department_scope(user, department_id)
    statement = (
        select(Position)
        .options(
            joinedload(Position.department),
            selectinload(Position.functions),
        )
        .where(Position.active.is_(True))
        .order_by(Position.department_id, Position.title)
    )
    if scoped_department_id is not None:
        statement = statement.where(Position.department_id == scoped_department_id)
    return [present_position(item) for item in db.scalars(statement)]
