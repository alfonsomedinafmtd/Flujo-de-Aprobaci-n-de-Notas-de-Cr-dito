from tests.conftest import TEST_PASSWORD, login


def test_login_creates_httponly_session_and_returns_profile(test_context) -> None:
    client, _ = test_context

    response = client.post(
        "/api/auth/login",
        json={"username": "collab.a", "password": TEST_PASSWORD},
    )

    assert response.status_code == 200
    assert response.json()["user"]["role"] == "COLLABORATOR"
    cookie_header = response.headers["set-cookie"]
    assert "HttpOnly" in cookie_header
    assert "SameSite=lax" in cookie_header

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["department_name"] == "Departamento A"


def test_login_uses_generic_error_and_rejects_inactive_employee(test_context) -> None:
    client, _ = test_context

    invalid = client.post(
        "/api/auth/login",
        json={"username": "collab.a", "password": "incorrecta-123"},
    )
    inactive = client.post(
        "/api/auth/login",
        json={"username": "inactive.a", "password": TEST_PASSWORD},
    )

    assert invalid.status_code == 401
    assert invalid.json()["detail"] == "Usuario o contraseña inválidos"
    assert inactive.status_code == 403


def test_logout_requires_csrf_and_revokes_session(test_context) -> None:
    client, _ = test_context
    csrf_token = login(client, "collab.a")

    without_csrf = client.post("/api/auth/logout")
    assert without_csrf.status_code == 403

    logout = client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf_token})
    assert logout.status_code == 204
    assert client.get("/api/auth/me").status_code == 401
