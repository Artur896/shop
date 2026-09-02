import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import InvitationStatus, ListRole
from app.schemas.user import UserPublic


class InvitationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    list_id: uuid.UUID
    list_name: str | None = None
    sender: UserPublic | None = None
    receiver_id: uuid.UUID
    role: ListRole
    status: InvitationStatus
    expires_at: datetime
    created_at: datetime
