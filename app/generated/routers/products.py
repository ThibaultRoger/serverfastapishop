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
from app.generated.models import Product
from app.generated.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


def _get_or_404(session: SessionDep, id: uuid.UUID) -> Product:
    obj = session.get(Product, {"id": id})
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product introuvable")
    return obj


@router.get("", response_model=Page[ProductRead], summary="Lister products")
def list_products(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[ProductRead]:
    total = session.scalar(select(func.count()).select_from(Product)) or 0
    rows = session.scalars(
        select(Product)
        .order_by(Product.id)
        .limit(limit)
        .offset(offset)
    ).all()
    items = [ProductRead.model_validate(row) for row in rows]
    return Page[ProductRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/{id}", response_model=ProductRead, summary="Lire un élément de products")
def get_products(id: uuid.UUID, session: SessionDep) -> Product:
    return _get_or_404(session, id)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED, summary="Créer dans products")
def create_products(payload: ProductCreate, session: SessionDep) -> Product:
    obj = Product(**payload.model_dump(exclude_unset=True))
    session.add(obj)
    commit_or_rollback(session)
    session.refresh(obj)
    return obj


@router.patch("/{id}", response_model=ProductRead, summary="Modifier un élément de products")
def update_products(id: uuid.UUID, payload: ProductUpdate, session: SessionDep) -> Product:
    obj = _get_or_404(session, id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    commit_or_rollback(session)
    session.refresh(obj)
    return obj


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer un élément de products")
def delete_products(id: uuid.UUID, session: SessionDep) -> Response:
    obj = _get_or_404(session, id)
    session.delete(obj)
    commit_or_rollback(session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
