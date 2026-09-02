import json
import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.device import DeviceSubscription

logger = logging.getLogger(__name__)


async def send_push_to_user(db: AsyncSession, user_id: uuid.UUID, title: str, body: str, data: dict | None = None) -> None:
    if not settings.VAPID_PRIVATE_KEY:
        logger.info("push.skipped_no_vapid_key user_id=%s title=%s", user_id, title)
        return

    from pywebpush import WebPushException, webpush  # imported lazily: optional dependency at runtime

    result = await db.execute(select(DeviceSubscription).where(DeviceSubscription.user_id == user_id))
    subscriptions = result.scalars().all()
    payload = json.dumps({"title": title, "body": body, "data": data or {}})

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": settings.VAPID_SUBJECT},
            )
        except WebPushException as exc:
            logger.warning("push.delivery_failed endpoint=%s error=%s", sub.endpoint, exc)
