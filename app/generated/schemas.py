# Généré par fastapi-forge — NE PAS MODIFIER : régénéré par `forge sync`.
from __future__ import annotations

import datetime  # noqa: F401
import decimal  # noqa: F401
import uuid  # noqa: F401
from typing import Annotated, Any, Literal  # noqa: F401

from pydantic import BaseModel, ConfigDict, Field  # noqa: F401


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    label: str


class CategoryCreate(BaseModel):
    code: Annotated[str, Field(max_length=20)]
    label: Annotated[str, Field(max_length=100)]


class CategoryUpdate(BaseModel):
    label: Annotated[str | None, Field(max_length=100)] = None


class CustomerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_active: bool
    metadata_: Annotated[Any, Field(serialization_alias="metadata")]
    created_at: datetime.datetime


class CustomerCreate(BaseModel):
    email: Annotated[str, Field(max_length=255)]
    full_name: Annotated[str, Field(max_length=120)]
    is_active: bool = None  # défaut côté base si absent
    metadata_: Annotated[Any | None, Field(validation_alias="metadata")] = None
    created_at: datetime.datetime = None  # défaut côté base si absent


class CustomerUpdate(BaseModel):
    email: Annotated[str | None, Field(max_length=255)] = None
    full_name: Annotated[str | None, Field(max_length=120)] = None
    is_active: bool | None = None
    metadata_: Annotated[Any | None, Field(validation_alias="metadata")] = None
    created_at: datetime.datetime | None = None


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_id: int
    status: Literal['pending', 'paid', 'shipped', 'cancelled']
    ordered_at: datetime.datetime
    note: str | None


class OrderCreate(BaseModel):
    customer_id: int
    status: Literal['pending', 'paid', 'shipped', 'cancelled'] = None  # défaut côté base si absent
    ordered_at: datetime.datetime = None  # défaut côté base si absent
    note: str | None = None


class OrderUpdate(BaseModel):
    customer_id: int | None = None
    status: Literal['pending', 'paid', 'shipped', 'cancelled'] | None = None
    ordered_at: datetime.datetime | None = None
    note: str | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sku: str
    name: str
    price: decimal.Decimal
    category_code: str | None
    stock: int


class ProductCreate(BaseModel):
    sku: Annotated[str, Field(max_length=40)]
    name: Annotated[str, Field(max_length=200)]
    price: decimal.Decimal
    category_code: Annotated[str | None, Field(max_length=20)] = None
    stock: int = None  # défaut côté base si absent


class ProductUpdate(BaseModel):
    sku: Annotated[str | None, Field(max_length=40)] = None
    name: Annotated[str | None, Field(max_length=200)] = None
    price: decimal.Decimal | None = None
    category_code: Annotated[str | None, Field(max_length=20)] = None
    stock: int | None = None
