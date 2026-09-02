import uuid
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token, hash_token
from app.db.session import get_db
from app.models.ai import AIIntegration, AIToken
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise CREDENTIALS_EXCEPTION
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise CREDENTIALS_EXCEPTION from exc

    if payload.get("type") != "access":
        raise CREDENTIALS_EXCEPTION

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise CREDENTIALS_EXCEPTION from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user


class AIPrincipal:
    """The identity behind an AI-integration request: which user's data, which provider,
    and exactly which scopes this specific token was issued with."""

    def __init__(self, user: User, integration: AIIntegration, token: AIToken):
        self.user = user
        self.integration = integration
        self.token = token

    def has_scope(self, scope: str) -> bool:
        return scope in self.token.scopes

    def require_scope(self, scope: str) -> None:
        if not self.has_scope(scope):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"AI token is missing required scope: {scope}",
            )


async def get_ai_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> AIPrincipal:
    if credentials is None:
        raise CREDENTIALS_EXCEPTION

    token_hash = hash_token(credentials.credentials)
    result = await db.execute(select(AIToken).where(AIToken.token_hash == token_hash))
    token = result.scalar_one_or_none()
    if token is None or token.revoked_at is not None:
        raise CREDENTIALS_EXCEPTION
    if token.expires_at is not None and token.expires_at < datetime.now(timezone.utc):
        raise CREDENTIALS_EXCEPTION

    integration = await db.get(AIIntegration, token.integration_id)
    if integration is None or integration.status.value != "connected":
        raise CREDENTIALS_EXCEPTION

    user = await db.get(User, integration.user_id)
    if user is None:
        raise CREDENTIALS_EXCEPTION

    return AIPrincipal(user=user, integration=integration, token=token)
