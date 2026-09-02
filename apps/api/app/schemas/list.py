import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ListRole


class ListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    icon: str | None = None


class ListUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    icon: str | None = None


class ListSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    icon: str | None
    owner_id: uuid.UUID
    version: int
    created_at: datetime
    updated_at: datetime
    total_items: int = 0
    completed_items: int = 0
    my_role: ListRole = ListRole.VIEWER


class ListDetail(ListSummary):
    pass
