from datetime import date, timedelta

from sqlalchemy import select

from app.models import Position, UserAccount
from tests.conftest import login


def _create_note(client, csrf_token: str, *, amount: str, currency: str):
    return client.post(
        "/api/credit-notes",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "amount": amount,
            "currency": currency,
            "reason": "Solicitud para validar el panel analítico",
            "store_id": 1,
            "company_id": 1,
        },
    )


def test_analytics_is_restricted_to_admin(test_context) -> None:
    client, _ = test_context

    unauthenticated = client.get("/api/credit-notes/analytics")
    assert unauthenticated.status_code == 401

    login(client, "collab.a")
    collaborator = client.get("/api/credit-notes/analytics")
    assert collaborator.status_code == 403

    login(client, "head.a")
    department_head = client.get("/api/credit-notes/analytics")
    assert department_head.status_code == 403


def test_admin_analytics_aggregates_filters_and_preserves_position_snapshot(test_context) -> None:
    client, session_factory = test_context
    collaborator_csrf = login(client, "collab.a")
    usd_note = _create_note(client, collaborator_csrf, amount="120.50", currency="USD")
    ves_note = _create_note(client, collaborator_csrf, amount="350.00", currency="VES")
    assert usd_note.status_code == 201
    assert ves_note.status_code == 201
    assert usd_note.json()["requester_position_title"] == "Analista"

    with session_factory() as db:
        collaborator = db.scalar(select(UserAccount).where(UserAccount.username == "collab.a"))
        head_position = db.scalar(select(Position).where(Position.title == "Jefe"))
        assert collaborator is not None and head_position is not None
        collaborator.employee.position = head_position
        db.commit()

    head_csrf = login(client, "head.a")
    approved = client.post(
        f"/api/credit-notes/{usd_note.json()['id']}/approve",
        headers={"X-CSRF-Token": head_csrf},
        json={"expected_version": 1, "comment": "Aprobación para analítica"},
    )
    assert approved.status_code == 200

    login(client, "admin")
    response = client.get("/api/credit-notes/analytics")
    assert response.status_code == 200, response.text
    analytics = response.json()

    assert analytics["summary"]["total"] == 2
    assert analytics["summary"]["pending"] == 1
    assert analytics["summary"]["approved"] == 1
    assert analytics["summary"]["approval_rate"] == 100.0
    assert {item["currency"] for item in analytics["amounts"]} == {"USD", "VES"}
    amounts = {item["currency"]: item for item in analytics["amounts"]}
    assert amounts["USD"]["total_amount"] == "120.50"
    assert amounts["USD"]["average_amount"] == "120.50"
    assert amounts["VES"]["total_amount"] == "350.00"
    assert analytics["by_department"][0]["label"] == "Departamento A"
    assert analytics["by_position"][0]["label"] == "Analista"
    assert analytics["by_requester"][0]["username"] == "collab.a"
    assert analytics["by_requester"][0]["position_title"] == "Analista"
    assert analytics["oldest_pending"][0]["id"] == ves_note.json()["id"]

    pending_only = client.get("/api/credit-notes/analytics?status=PENDING")
    assert pending_only.status_code == 200
    assert pending_only.json()["summary"]["total"] == 1
    assert pending_only.json()["summary"]["approved"] == 0

    today = date.today()
    future = today + timedelta(days=1)
    empty = client.get(f"/api/credit-notes/analytics?date_from={future.isoformat()}")
    assert empty.status_code == 200
    assert empty.json()["summary"]["total"] == 0
    assert empty.json()["departments"]

    invalid_range = client.get(
        "/api/credit-notes/analytics"
        f"?date_from={future.isoformat()}&date_to={today.isoformat()}"
    )
    assert invalid_range.status_code == 422
