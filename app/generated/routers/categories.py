# Généré par fastapi-forge — NE PAS MODIFIER : régénéré par `forge sync`.
# Pour du comportement spécifique, créer un router dans app/custom/routers/.
from __future__ import annotations

import datetime  # noqa: F401
import decimal  # noqa: F401
import uuid  # noqa: F401
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import func, select

from app.core.db import SessionDep, commit_or_rollback
from app.core.pagination import Page
from app.generated.models import Category
from app.generated.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _get_or_404(session: SessionDep, code: str) -> Category:
    obj = session.get(Category, {"code": code})
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category introuvable")
    return obj


@router.get("", response_model=Page[CategoryRead], summary="Lister categories")
def list_categories(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[CategoryRead]:
    total = session.scalar(select(func.count()).select_from(Category)) or 0
    rows = session.scalars(
        select(Category)
        .order_by(Category.code)
        .limit(limit)
        .offset(offset)
    ).all()
    items = [CategoryRead.model_validate(row) for row in rows]
    return Page[CategoryRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/{code}", response_model=CategoryRead, summary="Lire un élément de categories")
def get_categories(code: str, session: SessionDep) -> Category:
    return _get_or_404(session, code)


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, summary="Créer dans categories")
def create_categories(payload: CategoryCreate, session: SessionDep) -> Category:
    obj = Category(**payload.model_dump(exclude_unset=True))
    session.add(obj)
    commit_or_rollback(session)
    session.refresh(obj)
    return obj


@router.patch("/{code}", response_model=CategoryRead, summary="Modifier un élément de categories")
def update_categories(code: str, payload: CategoryUpdate, session: SessionDep) -> Category:
    obj = _get_or_404(session, code)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    commit_or_rollback(session)
    session.refresh(obj)
    return obj


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer un élément de categories")
def delete_categories(code: str, session: SessionDep) -> Response:
    obj = _get_or_404(session, code)
    session.delete(obj)
    commit_or_rollback(session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
