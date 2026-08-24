from collections.abc import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.enums import EmployeeStatus, Seniority, UserRole
from app.main import app
from app.models import Company, Department, Employee, Position, Store, UserAccount
from app.security import hash_password


TEST_PASSWORD = "Prueba-Segura-2026!"


@pytest.fixture
def test_context() -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    test_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(engine)

    with test_session() as db:
        department_a = Department(code="A", name="Departamento A", active=True)
        department_b = Department(code="B", name="Departamento B", active=True)
        position_a = Position(
            department=department_a,
            title="Analista",
            seniority=Seniority.SEMI_SENIOR,
            active=True,
        )
        head_position_a = Position(
            department=department_a,
            title="Jefe",
            seniority=Seniority.LEAD,
            active=True,
        )
        head_position_b = Position(
            department=department_b,
            title="Jefe",
            seniority=Seniority.LEAD,
            active=True,
        )
        admin_position = Position(
            department=department_b,
            title="Administrador",
            seniority=Seniority.LEAD,
            active=True,
        )
        db.add_all([department_a, department_b])
        db.flush()

        users = (
            ("collab.a", UserRole.COLLABORATOR, position_a, EmployeeStatus.ACTIVE),
            ("head.a", UserRole.DEPARTMENT_HEAD, head_position_a, EmployeeStatus.ACTIVE),
            ("head.b", UserRole.DEPARTMENT_HEAD, head_position_b, EmployeeStatus.ACTIVE),
            ("admin", UserRole.ADMIN, admin_position, EmployeeStatus.ACTIVE),
            ("inactive.a", UserRole.COLLABORATOR, position_a, EmployeeStatus.INACTIVE),
        )
        for index, (username, role, position, employee_status) in enumerate(users, start=1):
            employee = Employee(
                position=position,
                first_name="Persona",
                last_name=f"Prueba {index}",
                country="Venezuela",
                hire_date=date(2024, 1, index),
                internal_email=f"test{index}@example.invalid",
                status=employee_status,
            )
            db.add(employee)
            db.flush()
            db.add(
                UserAccount(
                    employee=employee,
                    username=username,
                    password_hash=hash_password(TEST_PASSWORD),
                    role=role,
                    active=True,
                )
            )

        db.add(Store(name="Tienda de Prueba", country="Venezuela", active=True))
        db.add(Company(name="Compañía de Prueba", industry="Pruebas", active=True))
        db.commit()

    def override_get_db() -> Generator[Session, None, None]:
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client, test_session
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def login(client: TestClient, username: str) -> str:
    client.cookies.clear()
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": TEST_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()["csrf_token"]

