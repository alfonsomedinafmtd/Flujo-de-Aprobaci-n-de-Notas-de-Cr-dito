from datetime import timedelta

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.config import get_settings
from app.dependencies import Auth, CsrfAuth, DbSession
from app.enums import EmployeeStatus
from app.models import AuthSession, Employee, Position, UserAccount, utc_now
from app.presenters import present_current_user
from app.schemas import CsrfResponse, CurrentUserRead, LoginRequest, LoginResponse
from app.security import digest_token, generate_token, hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["authentication"])
DUMMY_PASSWORD_HASH = hash_password(generate_token())


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: DbSession) -> LoginResponse:
    statement = (
        select(UserAccount)
        .where(UserAccount.username == payload.username)
        .options(
            joinedload(UserAccount.employee)
            .joinedload(Employee.position)
            .joinedload(Position.department)
        )
    )
    user = db.scalar(statement)
    candidate_hash = user.password_hash if user is not None else DUMMY_PASSWORD_HASH
    password_is_valid = verify_password(payload.password.get_secret_value(), candidate_hash)
    if user is None or not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos",
        )
    if (
        not user.active
        or user.employee.status is not EmployeeStatus.ACTIVE
        or not user.employee.position.active
        or not user.employee.position.department.active
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cuenta inactiva")

    raw_token = generate_token()
    csrf_token = generate_token()
    settings = get_settings()
    expires_at = utc_now() + timedelta(minutes=settings.session_expire_minutes)
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=digest_token(raw_token),
            csrf_hash=digest_token(csrf_token),
            expires_at=expires_at,
        )
    )
    db.commit()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=raw_token,
        max_age=settings.session_expire_minutes * 60,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )
    return LoginResponse(user=present_current_user(user), csrf_token=csrf_token)


@router.get("/me", response_model=CurrentUserRead)
def me(context: Auth) -> CurrentUserRead:
    return present_current_user(context.user)


@router.post("/csrf", response_model=CsrfResponse)
def refresh_csrf(context: Auth, db: DbSession) -> CsrfResponse:
    csrf_token = generate_token()
    context.session.csrf_hash = digest_token(csrf_token)
    db.commit()
    return CsrfResponse(csrf_token=csrf_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(context: CsrfAuth, response: Response, db: DbSession) -> None:
    context.session.revoked_at = utc_now()
    db.commit()
    response.delete_cookie(get_settings().session_cookie_name, path="/")
