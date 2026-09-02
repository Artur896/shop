from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.enums import AIProvider
from app.models.user import User
from app.schemas.integration import (
    IntegrationConnectRequest,
    IntegrationConnectResponse,
    IntegrationOut,
    IntegrationPermissionsUpdate,
)
from app.services import integrations_service

router = APIRouter(prefix="/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationOut])
async def get_integrations(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[IntegrationOut]:
    integrations = await integrations_service.list_integrations(db, user.id)
    await db.commit()
    return [IntegrationOut.model_validate(i) for i in integrations]


@router.post("/{provider}/connect", response_model=IntegrationConnectResponse)
async def connect(
    provider: AIProvider,
    payload: IntegrationConnectRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IntegrationConnectResponse:
    integration, token, scopes = await integrations_service.connect_integration(
        db, user.id, provider, payload.scopes
    )
    await db.commit()
    # `token` is returned exactly once, here — it is never stored in plaintext, never
    # logged, and never included in any other response (GET /integrations only ever
    # returns the hashed record's metadata).
    return IntegrationConnectResponse(
        integration=IntegrationOut.model_validate(integration), token=token, scopes=scopes
    )


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect(
    provider: AIProvider, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    await integrations_service.disconnect_integration(db, user.id, provider)
    await db.commit()


@router.get("/{provider}/permissions", response_model=IntegrationOut)
async def get_permissions(
    provider: AIProvider, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> IntegrationOut:
    integration = await integrations_service.get_or_create_integration(db, user.id, provider)
    await db.commit()
    return IntegrationOut.model_validate(integration)


@router.patch("/{provider}/permissions", response_model=IntegrationOut)
async def update_permissions(
    provider: AIProvider,
    payload: IntegrationPermissionsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> IntegrationOut:
    integration = await integrations_service.update_permissions(db, user.id, provider, payload.scopes)
    await db.commit()
    return IntegrationOut.model_validate(integration)
