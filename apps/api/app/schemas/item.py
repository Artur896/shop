import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    quantity: Decimal = Decimal("1")
    unit: str | None = None
    category: str = "otros"
    notes: str | None = None
    estimated_price: Decimal | None = None


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    quantity: Decimal | None = None
    unit: str | None = None
    category: str | None = None
    notes: str | None = None
    estimated_price: Decimal | None = None
    is_completed: bool | None = None
    version: int | None = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    list_id: uuid.UUID
    name: str
    quantity: Decimal
    unit: str | None
    category: str
    notes: str | None
    estimated_price: Decimal | None
    is_completed: bool
    version: int
    created_at: datetime
    updated_at: datetime
