from tests.conftest import login


def test_collaborator_directory_is_limited_to_own_department(test_context) -> None:
    client, _ = test_context
    login(client, "collab.a")

    own_directory = client.get("/api/organization/directory")
    foreign_directory = client.get("/api/organization/directory?department_id=2")

    assert own_directory.status_code == 200
    assert own_directory.json()
    assert {item["department_name"] for item in own_directory.json()} == {"Departamento A"}
    assert foreign_directory.status_code == 403


def test_admin_can_view_all_departments(test_context) -> None:
    client, _ = test_context
    login(client, "admin")

    departments = client.get("/api/organization/departments")

    assert departments.status_code == 200
    assert {item["code"] for item in departments.json()} == {"A", "B"}


def test_employee_detail_exposes_fictitious_contact_and_portal_role(test_context) -> None:
    client, _ = test_context
    login(client, "collab.a")

    profile = client.get("/api/organization/profile")

    assert profile.status_code == 200
    assert profile.json()["internal_email"] == "test1@example.invalid"
    assert profile.json()["username"] == "collab.a"
    assert profile.json()["portal_role"] == "COLLABORATOR"
