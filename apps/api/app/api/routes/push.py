from fastapi import APIRouter, Depends, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.device import DeviceSubscription
from app.models.user import User
from app.schemas.push import PushSubscribeRequest

router = APIRouter(prefix="/push", tags=["push"])


@router.get("/vapid-public-key")
async def get_vapid_public_key() -> dict[str, str]:
    return {"publicKey": settings.VAPID_PUBLIC_KEY}


@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def subscribe(
    payload: PushSubscribeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    existing = await db.execute(
        select(DeviceSubscription).where(DeviceSubscription.endpoint == payload.endpoint)
    )
    subscription = existing.scalar_one_or_none()
    if subscription is None:
        subscription = DeviceSubscription(
            user_id=user.id,
            endpoint=payload.endpoint,
            p256dh=payload.p256dh,
            auth=payload.auth,
            user_agent=payload.user_agent,
        )
        db.add(subscription)
    else:
        subscription.user_id = user.id
        subscription.p256dh = payload.p256dh
        subscription.auth = payload.auth
    await db.commit()
    return {"status": "subscribed"}


@router.delete("/subscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(
    endpoint: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    await db.execute(
        delete(DeviceSubscription).where(
            DeviceSubscription.endpoint == endpoint, DeviceSubscription.user_id == user.id
        )
    )
    await db.commit()
