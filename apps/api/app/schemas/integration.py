import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import AIIntegrationStatus, AIProvider


class IntegrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider: AIProvider
    status: AIIntegrationStatus
    granted_scopes: list[str]
    updated_at: datetime


class IntegrationConnectRequest(BaseModel):
    scopes: list[str] | None = None


class IntegrationConnectResponse(BaseModel):
    integration: IntegrationOut
    token: str
    scopes: list[str]


class IntegrationPermissionsUpdate(BaseModel):
    scopes: list[str]
