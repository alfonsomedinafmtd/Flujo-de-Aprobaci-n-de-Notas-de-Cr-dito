from datetime import timedelta

from sqlalchemy import func, select

from app.models import AuthSession, utc_now
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
    unknown = client.post(
        "/api/auth/login",
        json={"username": "no-existe", "password": "incorrecta-123"},
    )
    inactive = client.post(
        "/api/auth/login",
        json={"username": "inactive.a", "password": TEST_PASSWORD},
    )

    assert invalid.status_code == 401
    assert invalid.json()["detail"] == "Usuario o contraseña inválidos"
    assert unknown.status_code == 401
    assert unknown.json()["detail"] == invalid.json()["detail"]
    assert inactive.status_code == 403


def test_login_rejects_non_string_username_without_creating_session(test_context) -> None:
    client, test_session = test_context

    response = client.post(
        "/api/auth/login",
        json={"username": 12345, "password": TEST_PASSWORD},
    )

    assert response.status_code == 422
    with test_session() as db:
        assert db.scalar(select(func.count(AuthSession.id))) == 0


def test_logout_requires_csrf_and_revokes_session(test_context) -> None:
    client, _ = test_context
    csrf_token = login(client, "collab.a")

    without_csrf = client.post("/api/auth/logout")
    assert without_csrf.status_code == 403

    logout = client.post("/api/auth/logout", headers={"X-CSRF-Token": csrf_token})
    assert logout.status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_expired_session_is_rejected_by_current_user_endpoint(test_context) -> None:
    client, test_session = test_context
    login(client, "collab.a")

    with test_session() as db:
        auth_session = db.scalar(select(AuthSession))
        assert auth_session is not None
        auth_session.expires_at = utc_now() - timedelta(seconds=1)
        db.commit()

    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_authenticated_session_can_rotate_csrf_after_page_reload(test_context) -> None:
    client, _ = test_context
    previous_csrf = login(client, "collab.a")

    refreshed = client.post("/api/auth/csrf")

    assert refreshed.status_code == 200
    new_csrf = refreshed.json()["csrf_token"]
    assert new_csrf != previous_csrf
    assert client.post("/api/auth/logout", headers={"X-CSRF-Token": previous_csrf}).status_code == 403
    assert client.post("/api/auth/logout", headers={"X-CSRF-Token": new_csrf}).status_code == 204
