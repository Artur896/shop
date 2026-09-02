import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.permissions.scopes import sanitize_scopes
from app.core.security import generate_ai_token
from app.models.ai import AIIntegration, AIToken
from app.models.enums import AIIntegrationStatus, AIProvider


async def get_or_create_integration(
    db: AsyncSession, user_id: uuid.UUID, provider: AIProvider
) -> AIIntegration:
    result = await db.execute(
        select(AIIntegration).where(AIIntegration.user_id == user_id, AIIntegration.provider == provider)
    )
    integration = result.scalar_one_or_none()
    if integration is None:
        integration = AIIntegration(user_id=user_id, provider=provider, granted_scopes=[])
        db.add(integration)
        await db.flush()
    return integration


async def list_integrations(db: AsyncSession, user_id: uuid.UUID) -> list[AIIntegration]:
    result = await db.execute(select(AIIntegration).where(AIIntegration.user_id == user_id))
    existing = {i.provider: i for i in result.scalars().all()}
    # Always show all providers, even ones the user has never touched, so the
    # "Integraciones" screen can render a full "Connected / Not connected" list.
    for provider in AIProvider:
        if provider not in existing:
            integration = AIIntegration(user_id=user_id, provider=provider, granted_scopes=[])
            db.add(integration)
            existing[provider] = integration
    await db.flush()
    return list(existing.values())


async def connect_integration(
    db: AsyncSession, user_id: uuid.UUID, provider: AIProvider, requested_scopes: list[str] | None
) -> tuple[AIIntegration, str, list[str]]:
    integration = await get_or_create_integration(db, user_id, provider)
    scopes = sanitize_scopes(requested_scopes)

    integration.status = AIIntegrationStatus.CONNECTED
    integration.granted_scopes = scopes

    plaintext, token_hash = generate_ai_token()
    token = AIToken(
        integration_id=integration.id,
        token_hash=token_hash,
        scopes=scopes,
        created_at=datetime.now(timezone.utc),
    )
    db.add(token)
    await db.flush()
    return integration, plaintext, scopes


async def disconnect_integration(db: AsyncSession, user_id: uuid.UUID, provider: AIProvider) -> None:
    integration = await get_or_create_integration(db, user_id, provider)
    integration.status = AIIntegrationStatus.DISCONNECTED
    for token in list(integration.tokens):
        if token.revoked_at is None:
            token.revoked_at = datetime.now(timezone.utc)
    await db.flush()


async def update_permissions(
    db: AsyncSession, user_id: uuid.UUID, provider: AIProvider, scopes: list[str]
) -> AIIntegration:
    integration = await get_or_create_integration(db, user_id, provider)
    if integration.status != AIIntegrationStatus.CONNECTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Integration is not connected")

    clean_scopes = sanitize_scopes(scopes)
    integration.granted_scopes = clean_scopes
    # Existing live tokens keep whatever scopes they were issued with (least-surprise:
    # revoking a scope here narrows what *new* tokens get; to hard-revoke immediately,
    # disconnect and reconnect the integration).
    await db.flush()
    return integration
