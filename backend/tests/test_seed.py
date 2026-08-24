from collections import Counter

from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import seed as seed_module
from app.database import Base
from app.enums import CreditNoteStatus
from app.models import CreditNote, CreditNoteEvent, Department, Employee, Position, UserAccount


def test_seed_creates_required_dataset_and_is_idempotent(monkeypatch, capsys) -> None:
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

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(seed_module, "SessionLocal", session_factory)

    try:
        seed_module.seed_database()
        first_output = capsys.readouterr().out

        with session_factory() as db:
            assert db.scalar(select(func.count(Department.id))) == 4
            assert db.scalar(select(func.count(Employee.id))) == 33
            assert db.scalar(select(func.count(UserAccount.id))) == 33
            assert db.scalar(select(func.count(CreditNote.id))) == 25

            employee_counts = dict(
                db.execute(
                    select(Department.code, func.count(Employee.id))
                    .join(Position, Position.department_id == Department.id)
                    .join(Employee, Employee.position_id == Position.id)
                    .group_by(Department.code)
                ).all()
            )
            assert employee_counts == {"CXC": 8, "CXP": 8, "PLN": 9, "TES": 8}
            assert all(8 <= count <= 12 for count in employee_counts.values())

            expected_statuses = Counter(note.status for note in seed_module.NOTES)
            actual_statuses = dict(
                db.execute(
                    select(CreditNote.status, func.count(CreditNote.id)).group_by(CreditNote.status)
                ).all()
            )
            assert actual_statuses == expected_statuses

            resolved_count = sum(
                note.status is not CreditNoteStatus.PENDING for note in seed_module.NOTES
            )
            assert db.scalar(select(func.count(CreditNoteEvent.id))) == 25 + resolved_count
            assert db.scalar(
                select(func.count(CreditNoteEvent.id)).where(
                    CreditNoteEvent.actor_user_id.is_(None),
                )
            ) == 0

        assert "4 departamentos, 33 colaboradores y 25 notas de crédito" in first_output

        seed_module.seed_database()
        second_output = capsys.readouterr().out
        assert "no se aplicó nuevamente el seed" in second_output

        with session_factory() as db:
            assert db.scalar(select(func.count(Employee.id))) == 33
            assert db.scalar(select(func.count(CreditNote.id))) == 25
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
