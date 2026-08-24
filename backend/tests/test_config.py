import pytest
from pydantic import ValidationError

from app.config import Settings


def test_production_requires_secure_cookie() -> None:
    with pytest.raises(ValidationError, match="SESSION_COOKIE_SECURE"):
        Settings(_env_file=None, environment="production", session_cookie_secure=False)


def test_cors_rejects_wildcard_with_credentials() -> None:
    with pytest.raises(ValidationError, match="CORS_ORIGINS"):
        Settings(_env_file=None, cors_origins="*")

