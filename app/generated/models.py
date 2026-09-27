# Généré par fastapi-forge — NE PAS MODIFIER : régénéré par `forge sync`.
# Schéma « public », empreinte 6562d594d86bd81c.
from __future__ import annotations

import datetime  # noqa: F401
import decimal  # noqa: F401
import uuid  # noqa: F401
from typing import Any  # noqa: F401

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg  # noqa: F401
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Category(Base):
    __tablename__ = "categories"

    code: Mapped[str] = mapped_column(sa.String(length=20), primary_key=True, autoincrement=False)
    label: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True, server_default=sa.FetchedValue())
    email: Mapped[str] = mapped_column(sa.String(length=255), nullable=False)
    full_name: Mapped[str] = mapped_column(sa.String(length=120), nullable=False)
    is_active: Mapped[bool] = mapped_column(sa.Boolean(), nullable=False, server_default=sa.FetchedValue())
    metadata_: Mapped[Any] = mapped_column('metadata', pg.JSONB(astext_type=sa.Text()), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(pg.TIMESTAMP(timezone=True), nullable=False, server_default=sa.FetchedValue())


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(sa.Integer(), primary_key=True, server_default=sa.FetchedValue())
    customer_id: Mapped[int] = mapped_column(sa.BigInteger(), sa.ForeignKey("customers.id"), nullable=False)
    status: Mapped[str] = mapped_column(pg.ENUM('pending', 'paid', 'shipped', 'cancelled', name='order_status', create_type=False), nullable=False, server_default=sa.FetchedValue())
    ordered_at: Mapped[datetime.datetime] = mapped_column(pg.TIMESTAMP(timezone=True), nullable=False, server_default=sa.FetchedValue())
    note: Mapped[str | None] = mapped_column(sa.Text(), nullable=True)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[uuid.UUID] = mapped_column(sa.Uuid(), primary_key=True, server_default=sa.FetchedValue())
    sku: Mapped[str] = mapped_column(sa.String(length=40), nullable=False)
    name: Mapped[str] = mapped_column(sa.String(length=200), nullable=False)
    price: Mapped[decimal.Decimal] = mapped_column(sa.Numeric(precision=10, scale=2), nullable=False)
    category_code: Mapped[str | None] = mapped_column(sa.String(length=20), sa.ForeignKey("categories.code"), nullable=True)
    stock: Mapped[int] = mapped_column(sa.Integer(), nullable=False, server_default=sa.FetchedValue())
