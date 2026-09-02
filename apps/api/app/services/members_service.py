import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ListRole, MemberStatus, NotificationType
from app.models.member import ListMember
from app.schemas.member import MemberOut
from app.services.authz import require_role
from app.services.notifications_service import notify
from app.ws.redis_pubsub import publish_list_event


async def list_members(db: AsyncSession, list_id: uuid.UUID, user_id: uuid.UUID) -> list[ListMember]:
    await require_role(db, list_id, user_id, ListRole.VIEWER)
    result = await db.execute(
        select(ListMember).where(
            ListMember.list_id == list_id, ListMember.status == MemberStatus.ACTIVE
        )
    )
    return list(result.scalars().all())


async def remove_member(
    db: AsyncSession, list_id: uuid.UUID, acting_user_id: uuid.UUID, target_user_id: uuid.UUID
) -> None:
    shopping_list, _ = await require_role(db, list_id, acting_user_id, ListRole.OWNER)
    if shopping_list.owner_id == target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the owner")

    result = await db.execute(
        select(ListMember).where(ListMember.list_id == list_id, ListMember.user_id == target_user_id)
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    member.status = MemberStatus.REMOVED
    await db.flush()

    await notify(
        db,
        target_user_id,
        NotificationType.MEMBER_REMOVED,
        title="Se te removió de una lista",
        message=f'Ya no tienes acceso a "{shopping_list.name}"',
        data={"list_id": str(list_id)},
    )
    await publish_list_event(list_id, "MEMBER_REMOVED", {"user_id": str(target_user_id)})


async def update_member_role(
    db: AsyncSession,
    list_id: uuid.UUID,
    acting_user_id: uuid.UUID,
    target_user_id: uuid.UUID,
    role: ListRole,
) -> ListMember:
    shopping_list, _ = await require_role(db, list_id, acting_user_id, ListRole.OWNER)
    if shopping_list.owner_id == target_user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change the owner's role")

    result = await db.execute(
        select(ListMember).where(ListMember.list_id == list_id, ListMember.user_id == target_user_id)
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    member.role = role
    await db.flush()
    return member
