from sqlalchemy import func, select

from app.enums import CreditNoteStatus
from app.models import CreditNote, CreditNoteEvent, UserAccount
from tests.conftest import login


def create_note(client, csrf_token: str):
    return client.post(
        "/api/credit-notes",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "amount": "1250.50",
            "currency": "USD",
            "reason": "Ajuste por diferencia de facturación",
            "store_id": 1,
            "company_id": 1,
        },
    )


def test_complete_approval_flow_records_actor_and_history(test_context) -> None:
    client, _ = test_context
    collaborator_csrf = login(client, "collab.a")
    created = create_note(client, collaborator_csrf)

    assert created.status_code == 201, created.text
    created_note = created.json()
    assert created_note["status"] == "PENDING"
    assert created_note["requesting_department"]["code"] == "A"
    assert created_note["creator_username"] == "collab.a"
    assert len(created_note["events"]) == 1

    head_csrf = login(client, "head.a")
    approved = client.post(
        f"/api/credit-notes/{created_note['id']}/approve",
        headers={"X-CSRF-Token": head_csrf},
        json={"expected_version": 1, "comment": "Soporte validado"},
    )

    assert approved.status_code == 200, approved.text
    approved_note = approved.json()
    assert approved_note["status"] == "APPROVED"
    assert approved_note["version"] == 2
    assert len(approved_note["events"]) == 2
    assert approved_note["events"][1]["actor_username"] == "head.a"
    assert approved_note["events"][1]["previous_status"] == "PENDING"

    repeated = client.post(
        f"/api/credit-notes/{created_note['id']}/approve",
        headers={"X-CSRF-Token": head_csrf},
        json={"expected_version": 1},
    )
    assert repeated.status_code == 409


def test_department_scope_is_enforced_in_backend(test_context) -> None:
    client, _ = test_context
    collaborator_csrf = login(client, "collab.a")
    note_id = create_note(client, collaborator_csrf).json()["id"]

    other_head_csrf = login(client, "head.b")
    detail = client.get(f"/api/credit-notes/{note_id}")
    approval = client.post(
        f"/api/credit-notes/{note_id}/approve",
        headers={"X-CSRF-Token": other_head_csrf},
        json={"expected_version": 1},
    )

    assert detail.status_code == 404
    assert approval.status_code == 404


def test_collaborator_cannot_approve_and_rejection_requires_comment(test_context) -> None:
    client, _ = test_context
    collaborator_csrf = login(client, "collab.a")
    note_id = create_note(client, collaborator_csrf).json()["id"]

    forbidden = client.post(
        f"/api/credit-notes/{note_id}/approve",
        headers={"X-CSRF-Token": collaborator_csrf},
        json={"expected_version": 1},
    )
    assert forbidden.status_code == 403

    head_csrf = login(client, "head.a")
    missing_comment = client.post(
        f"/api/credit-notes/{note_id}/reject",
        headers={"X-CSRF-Token": head_csrf},
        json={"expected_version": 1},
    )
    assert missing_comment.status_code == 422


def test_client_cannot_override_requesting_department(test_context) -> None:
    client, _ = test_context
    csrf_token = login(client, "collab.a")
    response = client.post(
        "/api/credit-notes",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "amount": "99.99",
            "currency": "USD",
            "reason": "Intento de cambiar el departamento",
            "store_id": 1,
            "company_id": 1,
            "requesting_department_id": 2,
        },
    )

    assert response.status_code == 422


def test_admin_can_decide_across_departments(test_context) -> None:
    client, _ = test_context
    collaborator_csrf = login(client, "collab.a")
    note_id = create_note(client, collaborator_csrf).json()["id"]

    admin_csrf = login(client, "admin")
    response = client.post(
        f"/api/credit-notes/{note_id}/approve",
        headers={"X-CSRF-Token": admin_csrf},
        json={"expected_version": 1, "comment": "Revisión global documentada"},
    )

    assert response.status_code == 200
    assert response.json()["events"][-1]["actor_username"] == "admin"


def test_autoapproval_is_rejected_even_for_inconsistent_imported_data(test_context) -> None:
    client, session_factory = test_context
    collaborator_csrf = login(client, "collab.a")
    note_id = create_note(client, collaborator_csrf).json()["id"]

    with session_factory() as db:
        note = db.get(CreditNote, note_id)
        head = db.scalar(select(UserAccount).where(UserAccount.username == "head.a"))
        assert note is not None and head is not None
        note.created_by_user_id = head.id
        db.commit()

    head_csrf = login(client, "head.a")
    response = client.post(
        f"/api/credit-notes/{note_id}/approve",
        headers={"X-CSRF-Token": head_csrf},
        json={"expected_version": 1},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "No se permite la autoaprobación"


def test_credit_note_creation_requires_csrf(test_context) -> None:
    client, session_factory = test_context
    login(client, "collab.a")

    response = client.post(
        "/api/credit-notes",
        json={
            "amount": "1250.50",
            "currency": "USD",
            "reason": "Solicitud sin token CSRF",
            "store_id": 1,
            "company_id": 1,
        },
    )

    assert response.status_code == 403
    with session_factory() as db:
        assert db.scalar(select(func.count(CreditNote.id))) == 0


def test_stale_version_does_not_change_state_or_append_audit_event(test_context) -> None:
    client, session_factory = test_context
    collaborator_csrf = login(client, "collab.a")
    note_id = create_note(client, collaborator_csrf).json()["id"]

    head_csrf = login(client, "head.a")
    response = client.post(
        f"/api/credit-notes/{note_id}/approve",
        headers={"X-CSRF-Token": head_csrf},
        json={"expected_version": 2, "comment": "Vista desactualizada"},
    )

    assert response.status_code == 409
    with session_factory() as db:
        note = db.get(CreditNote, note_id)
        event_count = db.scalar(
            select(func.count(CreditNoteEvent.id)).where(
                CreditNoteEvent.credit_note_id == note_id,
            )
        )
        assert note is not None
        assert note.status is CreditNoteStatus.PENDING
        assert note.version == 1
        assert event_count == 1
