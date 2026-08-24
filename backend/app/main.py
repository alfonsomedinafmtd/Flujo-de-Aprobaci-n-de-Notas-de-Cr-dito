from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth, credit_notes, organization


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="API para estructura organizacional y flujo auditable de notas de crédito.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-CSRF-Token"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(organization.router, prefix="/api")
app.include_router(credit_notes.router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}

