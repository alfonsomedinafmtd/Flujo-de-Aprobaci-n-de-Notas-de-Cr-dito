from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, select

from app.database import SessionLocal
from app.enums import (
    CreditNoteAction,
    CreditNoteStatus,
    Currency,
    EmployeeStatus,
    Seniority,
    UserRole,
)
from app.models import (
    BusinessFunction,
    Company,
    CreditNote,
    CreditNoteEvent,
    Department,
    Employee,
    Position,
    Store,
    UserAccount,
)
from app.security import hash_password


DEPARTMENTS = (
    ("CXC", "Cuentas por Cobrar", "Gestión y conciliación de cuentas por cobrar."),
    ("CXP", "Cuentas por Pagar", "Control y programación de obligaciones con proveedores."),
    ("PLN", "Planificación Financiera", "Presupuesto, proyecciones y análisis financiero."),
    ("TES", "Tesorería", "Liquidez, pagos y administración de fondos."),
)

FUNCTIONS = (
    ("ANALYSIS", "Análisis financiero", "Analizar información y explicar variaciones."),
    ("CONTROL", "Control documental", "Validar soportes y cumplimiento del proceso."),
    ("RECONCILIATION", "Conciliación", "Conciliar operaciones con registros financieros."),
    ("APPROVAL", "Aprobación", "Decidir solicitudes dentro del alcance autorizado."),
    ("PLANNING", "Planificación", "Preparar escenarios y proyecciones."),
    ("REPORTING", "Reportes", "Preparar reportes trazables para la gestión."),
)

EMPLOYEES_BY_DEPARTMENT = {
    "CXC": (
        ("Helena", "Prisma"),
        ("Ariel", "Cedro"),
        ("Bianca", "Lago"),
        ("Camilo", "Brisa"),
        ("Dana", "Roble"),
        ("Elio", "Nube"),
        ("Flora", "Menta"),
        ("Gael", "Sol"),
    ),
    "CXP": (
        ("Inés", "Vector"),
        ("Julián", "Álamo"),
        ("Kiara", "Delta"),
        ("León", "Coral"),
        ("Mara", "Lumen"),
        ("Nilo", "Prado"),
        ("Olga", "Sierra"),
        ("Piero", "Cauce"),
    ),
    "PLN": (
        ("Raúl", "Métrica"),
        ("Sara", "Quanta"),
        ("Teo", "Atlas"),
        ("Uma", "Cifra"),
        ("Vera", "Plan"),
        ("Walter", "Faro"),
        ("Ximena", "Norte"),
        ("Yago", "Orbe"),
    ),
    "TES": (
        ("Zoe", "Balance"),
        ("Alma", "Risco"),
        ("Bruno", "Claro"),
        ("Cora", "Duna"),
        ("Dante", "Pulso"),
        ("Eva", "Llano"),
        ("Fabio", "Monte"),
        ("Gina", "Ruta"),
    ),
}

STORES = (
    ("Tienda Chacao", "Venezuela"),
    ("Tienda Las Mercedes", "Venezuela"),
    ("Tienda Maracaibo Centro", "Venezuela"),
    ("Tienda Palermo", "Argentina"),
    ("Tienda Belgrano", "Argentina"),
    ("Tienda Córdoba Norte", "Argentina"),
)

COMPANIES = (
    ("Laboratorios Andina C.A.", "Farmacéutico"),
    ("Distribuidora Cuyaní", "Cuidado personal"),
    ("Nutrisana Import", "Nutrición y suplementos"),
    ("Grupo Farmavalle", "Farmacéutico"),
    ("Beltek Consumo Masivo", "Consumo masivo"),
    ("Salud Total Distribución", "Farmacéutico"),
)


@dataclass(frozen=True)
class NoteSeed:
    amount: str
    currency: Currency
    reason: str
    store_id: int
    company_id: int
    department_code: str
    status: CreditNoteStatus
    created_at: str
    decided_at: str | None = None


NOTES = (
    NoteSeed("1262.21", Currency.USD, "Error de facturación en monto despachado", 6, 1, "CXC", CreditNoteStatus.APPROVED, "2026-05-18", "2026-05-22"),
    NoteSeed("1132.26", Currency.USD, "Producto recibido en mal estado", 5, 4, "CXC", CreditNoteStatus.PENDING, "2026-07-04"),
    NoteSeed("2966.87", Currency.USD, "Diferencia cambiaria en pago anticipado a proveedor", 6, 6, "CXP", CreditNoteStatus.PENDING, "2026-05-01"),
    NoteSeed("3829.30", Currency.USD, "Diferencia cambiaria en pago anticipado a proveedor", 3, 3, "CXC", CreditNoteStatus.PENDING, "2026-05-14"),
    NoteSeed("4045.28", Currency.USD, "Diferencia cambiaria en pago anticipado a proveedor", 1, 3, "CXP", CreditNoteStatus.APPROVED, "2026-06-28", "2026-07-02"),
    NoteSeed("3111.67", Currency.USD, "Error de facturación en monto despachado", 1, 5, "CXP", CreditNoteStatus.REJECTED, "2026-06-16", "2026-06-18"),
    NoteSeed("4926.85", Currency.USD, "Diferencia cambiaria en pago anticipado a proveedor", 1, 6, "CXC", CreditNoteStatus.APPROVED, "2026-05-30", "2026-05-31"),
    NoteSeed("1808.59", Currency.VES, "Error de facturación en monto despachado", 3, 4, "CXP", CreditNoteStatus.PENDING, "2026-07-25"),
    NoteSeed("1261.81", Currency.VES, "Duplicidad de despacho a la misma tienda", 5, 6, "CXC", CreditNoteStatus.APPROVED, "2026-06-29", "2026-06-30"),
    NoteSeed("4222.12", Currency.USD, "Devolución de producto por vencimiento", 6, 6, "CXC", CreditNoteStatus.APPROVED, "2026-05-08", "2026-05-12"),
    NoteSeed("4570.02", Currency.VES, "Producto recibido en mal estado", 3, 4, "CXP", CreditNoteStatus.PENDING, "2026-07-12"),
    NoteSeed("3232.12", Currency.VES, "Ajuste de precio por promoción no aplicada", 6, 4, "CXP", CreditNoteStatus.REJECTED, "2026-05-19", "2026-05-22"),
    NoteSeed("2170.75", Currency.VES, "Descuento comercial no reflejado en factura", 2, 6, "CXP", CreditNoteStatus.APPROVED, "2026-07-14", "2026-07-18"),
    NoteSeed("283.23", Currency.USD, "Ajuste de precio por promoción no aplicada", 2, 2, "CXP", CreditNoteStatus.PENDING, "2026-05-15"),
    NoteSeed("2999.65", Currency.VES, "Devolución de producto por vencimiento", 6, 4, "CXC", CreditNoteStatus.APPROVED, "2026-06-29", "2026-07-03"),
    NoteSeed("2708.00", Currency.VES, "Error de facturación en monto despachado", 6, 6, "CXC", CreditNoteStatus.APPROVED, "2026-06-04", "2026-06-08"),
    NoteSeed("4771.39", Currency.USD, "Error de facturación en monto despachado", 3, 4, "CXC", CreditNoteStatus.APPROVED, "2026-06-03", "2026-06-04"),
    NoteSeed("3824.43", Currency.USD, "Descuento comercial no reflejado en factura", 6, 3, "CXC", CreditNoteStatus.PENDING, "2026-07-09"),
    NoteSeed("4399.67", Currency.USD, "Devolución de producto por vencimiento", 4, 1, "CXC", CreditNoteStatus.REJECTED, "2026-06-09", "2026-06-10"),
    NoteSeed("2455.65", Currency.USD, "Ajuste de precio por promoción no aplicada", 2, 5, "CXC", CreditNoteStatus.PENDING, "2026-05-09"),
    NoteSeed("4368.54", Currency.USD, "Producto recibido en mal estado", 6, 4, "CXC", CreditNoteStatus.PENDING, "2026-06-24"),
    NoteSeed("3266.90", Currency.VES, "Error de facturación en monto despachado", 6, 3, "CXP", CreditNoteStatus.REJECTED, "2026-06-26", "2026-06-27"),
    NoteSeed("2962.13", Currency.USD, "Devolución de producto por vencimiento", 2, 2, "CXC", CreditNoteStatus.PENDING, "2026-05-30"),
    NoteSeed("4531.83", Currency.USD, "Producto recibido en mal estado", 1, 6, "CXC", CreditNoteStatus.PENDING, "2026-06-12"),
    NoteSeed("704.94", Currency.VES, "Producto recibido en mal estado", 3, 6, "CXP", CreditNoteStatus.PENDING, "2026-07-13"),
)


def _demo_password(label: str) -> str:
    return f"{label}-{secrets.token_urlsafe(12)}"


def _position_key(employee_index: int) -> str:
    if employee_index == 0:
        return "head"
    if employee_index in {1, 2}:
        return "senior"
    if employee_index in {3, 4, 5}:
        return "analyst"
    return "assistant"


def seed_database() -> None:
    db = SessionLocal()
    try:
        if (db.scalar(select(func.count(Department.id))) or 0) > 0:
            print("La base ya contiene departamentos; no se aplicó nuevamente el seed.")
            return

        admin_password = _demo_password("Admin")
        head_password = _demo_password("Jefe")
        collaborator_password = _demo_password("Colaborador")

        functions = {
            code: BusinessFunction(code=code, name=name, description=description)
            for code, name, description in FUNCTIONS
        }
        db.add_all(functions.values())

        departments = {
            code: Department(code=code, name=name, description=description, active=True)
            for code, name, description in DEPARTMENTS
        }
        db.add_all(departments.values())
        db.flush()

        position_map: dict[tuple[str, str], Position] = {}
        function_sets = {
            "head": [functions["CONTROL"], functions["APPROVAL"], functions["REPORTING"]],
            "senior": [functions["ANALYSIS"], functions["RECONCILIATION"], functions["REPORTING"]],
            "analyst": [functions["ANALYSIS"], functions["RECONCILIATION"]],
            "assistant": [functions["CONTROL"], functions["REPORTING"]],
        }
        seniorities = {
            "head": Seniority.LEAD,
            "senior": Seniority.SENIOR,
            "analyst": Seniority.SEMI_SENIOR,
            "assistant": Seniority.ASSISTANT,
        }
        titles = {
            "head": "Jefe de Departamento",
            "senior": "Analista Senior",
            "analyst": "Analista Financiero",
            "assistant": "Asistente Financiero",
        }
        for department_code, department in departments.items():
            for key in ("head", "senior", "analyst", "assistant"):
                position = Position(
                    department=department,
                    title=titles[key],
                    seniority=seniorities[key],
                    description=f"{titles[key]} de {department.name}.",
                    functions=list(function_sets[key]),
                    active=True,
                )
                position_map[(department_code, key)] = position
                db.add(position)

        admin_position = Position(
            department=departments["PLN"],
            title="Administrador del Portal",
            seniority=Seniority.LEAD,
            description="Administración funcional y supervisión global del portal.",
            functions=[functions["CONTROL"], functions["REPORTING"]],
            active=True,
        )
        db.add(admin_position)
        db.flush()

        admin_employee = Employee(
            position=admin_position,
            first_name="Ada",
            last_name="Horizonte",
            country="Venezuela",
            hire_date=date(2021, 2, 8),
            internal_email="ada.horizonte@example.invalid",
            status=EmployeeStatus.ACTIVE,
        )
        db.add(admin_employee)
        db.flush()
        db.add(
            UserAccount(
                employee=admin_employee,
                username="admin",
                password_hash=hash_password(admin_password),
                role=UserRole.ADMIN,
                active=True,
            )
        )

        users: dict[str, UserAccount] = {}
        countries = ("Venezuela", "Argentina")
        for department_code, names in EMPLOYEES_BY_DEPARTMENT.items():
            for index, (first_name, last_name) in enumerate(names):
                key = _position_key(index)
                inactive = index == 7 and department_code in {"CXP", "TES"}
                employee = Employee(
                    position=position_map[(department_code, key)],
                    first_name=first_name,
                    last_name=last_name,
                    country=countries[index % len(countries)],
                    hire_date=date(2018 + (index % 7), (index % 12) + 1, min(5 + index, 28)),
                    internal_email=f"{department_code.lower()}.{index:02d}@example.invalid",
                    status=EmployeeStatus.INACTIVE if inactive else EmployeeStatus.ACTIVE,
                )
                db.add(employee)
                db.flush()
                if index == 0:
                    username = f"jefe.{department_code.lower()}"
                    role = UserRole.DEPARTMENT_HEAD
                    password = head_password
                else:
                    username = f"{department_code.lower()}{index:02d}"
                    role = UserRole.COLLABORATOR
                    password = collaborator_password
                user = UserAccount(
                    employee=employee,
                    username=username,
                    password_hash=hash_password(password),
                    role=role,
                    active=True,
                )
                users[username] = user
                db.add(user)

        db.add_all(
            [Store(name=name, country=country, active=True) for name, country in STORES]
        )
        db.add_all(
            [Company(name=name, industry=industry, active=True) for name, industry in COMPANIES]
        )
        db.flush()

        creator_index = {"CXC": 1, "CXP": 1}
        for note_seed in NOTES:
            collab_number = creator_index[note_seed.department_code]
            creator_index[note_seed.department_code] = 1 + (collab_number % 6)
            creator = users[f"{note_seed.department_code.lower()}{collab_number:02d}"]
            head = users[f"jefe.{note_seed.department_code.lower()}"]
            created_at = datetime.fromisoformat(note_seed.created_at)
            updated_at = (
                datetime.fromisoformat(note_seed.decided_at)
                if note_seed.decided_at
                else created_at
            )
            note = CreditNote(
                amount=Decimal(note_seed.amount),
                currency=note_seed.currency,
                reason=note_seed.reason,
                requesting_department=departments[note_seed.department_code],
                creator=creator,
                store_id=note_seed.store_id,
                company_id=note_seed.company_id,
                status=note_seed.status,
                version=2 if note_seed.status is not CreditNoteStatus.PENDING else 1,
                created_at=created_at,
                updated_at=updated_at,
            )
            db.add(note)
            db.flush()
            db.add(
                CreditNoteEvent(
                    credit_note=note,
                    actor=creator,
                    action=CreditNoteAction.CREATED,
                    previous_status=None,
                    new_status=CreditNoteStatus.PENDING,
                    comment="Solicitud adaptada del dataset ficticio proporcionado.",
                    occurred_at=created_at,
                )
            )
            if note_seed.status is not CreditNoteStatus.PENDING:
                action = (
                    CreditNoteAction.APPROVED
                    if note_seed.status is CreditNoteStatus.APPROVED
                    else CreditNoteAction.REJECTED
                )
                comment = (
                    "Aprobada tras validar los soportes."
                    if note_seed.status is CreditNoteStatus.APPROVED
                    else "Rechazada por soporte documental insuficiente."
                )
                db.add(
                    CreditNoteEvent(
                        credit_note=note,
                        actor=head,
                        action=action,
                        previous_status=CreditNoteStatus.PENDING,
                        new_status=note_seed.status,
                        comment=comment,
                        occurred_at=updated_at,
                    )
                )

        db.commit()
        print("Seed completado: 4 departamentos, 33 colaboradores y 25 notas de crédito.")
        print("Credenciales demo generadas para esta base:")
        print(f"  admin / {admin_password}")
        print(f"  jefe.cxc (y demás jefes) / {head_password}")
        print(f"  cxc01 (y demás colaboradores) / {collaborator_password}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

