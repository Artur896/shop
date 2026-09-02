import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import ListRole, MemberStatus
from app.schemas.user import UserPublic


class MemberInviteRequest(BaseModel):
    email: EmailStr
    role: ListRole = ListRole.EDITOR


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    list_id: uuid.UUID
    user_id: uuid.UUID
    role: ListRole
    status: MemberStatus
    created_at: datetime
    user: UserPublic | None = None


class MemberRoleUpdate(BaseModel):
    role: ListRole
