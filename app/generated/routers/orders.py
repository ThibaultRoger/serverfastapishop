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
from app.generated.models import Order
from app.generated.schemas import OrderCreate, OrderRead, OrderUpdate

router = APIRouter(prefix="/orders", tags=["orders"])


def _get_or_404(session: SessionDep, id: int) -> Order:
    obj = session.get(Order, {"id": id})
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order introuvable")
    return obj


@router.get("", response_model=Page[OrderRead], summary="Lister orders")
def list_orders(
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Page[OrderRead]:
    total = session.scalar(select(func.count()).select_from(Order)) or 0
    rows = session.scalars(
        select(Order)
        .order_by(Order.id)
        .limit(limit)
        .offset(offset)
    ).all()
    items = [OrderRead.model_validate(row) for row in rows]
    return Page[OrderRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/{id}", response_model=OrderRead, summary="Lire un élément de orders")
def get_orders(id: int, session: SessionDep) -> Order:
    return _get_or_404(session, id)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED, summary="Créer dans orders")
def create_orders(payload: OrderCreate, session: SessionDep) -> Order:
    obj = Order(**payload.model_dump(exclude_unset=True))
    session.add(obj)
    commit_or_rollback(session)
    session.refresh(obj)
    return obj


@router.patch("/{id}", response_model=OrderRead, summary="Modifier un élément de orders")
def update_orders(id: int, payload: OrderUpdate, session: SessionDep) -> Order:
    obj = _get_or_404(session, id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    commit_or_rollback(session)
    session.refresh(obj)
    return obj


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer un élément de orders")
def delete_orders(id: int, session: SessionDep) -> Response:
    obj = _get_or_404(session, id)
    session.delete(obj)
    commit_or_rollback(session)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
