from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.core.config import settings
from app.core.db import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
def liveness() -> dict[str, str]:
    return {"status": "ok", "version": settings.app_version, "commit": settings.git_sha}


@router.get("/ready")
def readiness(session: SessionDep) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail="base de données indisponible") from exc
    return {"status": "ready"}
