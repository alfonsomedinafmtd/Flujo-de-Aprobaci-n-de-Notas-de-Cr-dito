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

