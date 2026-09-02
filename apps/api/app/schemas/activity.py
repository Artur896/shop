import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ActorType, AuditResult


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_type: ActorType
    actor_id: str
    action: str
    resource_type: str
    resource_id: str | None
    result: AuditResult
    created_at: datetime
