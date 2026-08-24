from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.database import get_db
from app.enums import EmployeeStatus, UserRole
from app.models import AuthSession, Employee, Position, UserAccount, utc_now
from app.security import digest_token, matches_digest


DbSession = Annotated[Session, Depends(get_db)]


@dataclass(frozen=True)
class AuthContext:
    user: UserAccount
    session: AuthSession

    @property
    def department_id(self) -> int:
        return self.user.employee.position.department_id


def get_auth_context(
    request: Request,
    db: DbSession,
) -> AuthContext:
    settings = get_settings()
    raw_token = request.cookies.get(settings.session_cookie_name)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Autenticación requerida")

    statement = (
        select(AuthSession)
        .where(AuthSession.token_hash == digest_token(raw_token))
        .options(
            joinedload(AuthSession.user)
            .joinedload(UserAccount.employee)
            .joinedload(Employee.position)
            .joinedload(Position.department)
        )
    )
    auth_session = db.scalar(statement)
    if (
        auth_session is None
        or auth_session.revoked_at is not None
        or auth_session.expires_at <= utc_now()
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión inválida o expirada")

    user = auth_session.user
    employee = user.employee
    if (
        not user.active
        or employee.status is not EmployeeStatus.ACTIVE
        or not employee.position.active
        or not employee.position.department.active
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta inactiva")

    return AuthContext(user=user, session=auth_session)


Auth = Annotated[AuthContext, Depends(get_auth_context)]


def get_current_user(context: Auth) -> UserAccount:
    return context.user


CurrentUser = Annotated[UserAccount, Depends(get_current_user)]


def require_csrf(
    context: Auth,
    csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> AuthContext:
    if not csrf_token or not matches_digest(csrf_token, context.session.csrf_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token CSRF inválido")
    return context


CsrfAuth = Annotated[AuthContext, Depends(require_csrf)]


def require_roles(*allowed_roles: UserRole):
    def dependency(user: CurrentUser) -> UserAccount:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso insuficiente")
        return user

    return dependency
