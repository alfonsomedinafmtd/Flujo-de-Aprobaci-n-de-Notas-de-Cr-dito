from functools import lru_cache

from pydantic import PositiveInt, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Portal de Finanzas"
    environment: str = "development"
    database_url: str = "sqlite:///./finance_portal.db"
    cors_origins: str = "http://localhost:5173"
    allowed_hosts: str = "localhost,127.0.0.1,testserver"
    session_cookie_name: str = "finance_session"
    session_expire_minutes: PositiveInt = 60
    session_cookie_secure: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_host_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if "*" in self.cors_origin_list:
            raise ValueError("CORS_ORIGINS no puede contener '*' cuando se usan cookies")
        if self.environment.lower() == "production" and not self.session_cookie_secure:
            raise ValueError("SESSION_COOKIE_SECURE debe ser true en producción")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
