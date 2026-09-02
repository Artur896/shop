import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import NotificationType
from app.models.notification import Notification


async def notify(
    db: AsyncSession,
    user_id: uuid.UUID,
    notif_type: NotificationType,
    title: str,
    message: str,
    data: dict | None = None,
) -> Notification:
    notification = Notification(
        user_id=user_id, type=notif_type, title=title, message=message, data=data or {}
    )
    db.add(notification)
    await db.flush()
    return notification
