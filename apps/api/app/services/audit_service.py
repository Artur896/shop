import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog
from app.models.enums import ActorType, AuditResult


async def record(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    actor_type: ActorType,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str | None,
    operation_id: str,
    result: AuditResult = AuditResult.SUCCESS,
    metadata: dict | None = None,
) -> AuditLog:
    """Every AI-driven mutation (and any other action worth auditing) is recorded here.
    `metadata` should stay free of sensitive payload content — names/ids/counts, not
    full product notes or personal data."""
    log = AuditLog(
        user_id=user_id,
        actor_type=actor_type,
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        operation_id=operation_id,
        result=result,
        metadata_=metadata or {},
    )
    db.add(log)
    await db.flush()
    return log
