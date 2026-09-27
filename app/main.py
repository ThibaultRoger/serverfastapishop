"""Point d'entrée FastAPI générique.

Les routers sont découverts automatiquement :
  1. app.custom.routers    (endpoints métier, prioritaires)
  2. app.generated.routers (CRUD déterministe produit par la forge)
Les routes custom passent en premier pour qu'une route fixe comme
/customers/stats ne soit pas capturée par /customers/{id}.
"""
from __future__ import annotations

import importlib
import logging
import pkgutil

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.api.health import router as health_router
from app.core.config import settings

logger = logging.getLogger(__name__)

ROUTER_PACKAGES = ("app.custom.routers", "app.generated.routers")


def discover_routers(package_name: str) -> list[APIRouter]:
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError:
        return []
    routers = []
    for module_info in sorted(pkgutil.iter_modules(package.__path__), key=lambda m: m.name):
        module = importlib.import_module(f"{package_name}.{module_info.name}")
        router = getattr(module, "router", None)
        if isinstance(router, APIRouter):
            routers.append(router)
        else:
            logger.warning("Module %s ignoré : pas de variable 'router'", module.__name__)
    return routers


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, version=settings.app_version, description=settings.app_description)
    app.include_router(health_router)
    for package_name in ROUTER_PACKAGES:
        for router in discover_routers(package_name):
            app.include_router(router)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(_: Request, exc: IntegrityError) -> JSONResponse:
        detail = str(exc.orig).splitlines()[0] if exc.orig else "Violation de contrainte"
        return JSONResponse(status_code=409, content={"detail": detail})

    return app


app = create_app()
