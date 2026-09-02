import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ListRole, MemberStatus
from app.models.list import ShoppingList
from app.models.member import ListMember

_ROLE_RANK = {ListRole.VIEWER: 0, ListRole.EDITOR: 1, ListRole.OWNER: 2}

NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="List not found")


async def get_list_or_404(db: AsyncSession, list_id: uuid.UUID) -> ShoppingList:
    result = await db.execute(select(ShoppingList).where(ShoppingList.id == list_id))
    shopping_list = result.scalar_one_or_none()
    if shopping_list is None:
        raise NOT_FOUND
    return shopping_list


async def resolve_role(db: AsyncSession, shopping_list: ShoppingList, user_id: uuid.UUID) -> ListRole | None:
    """The single source of truth for "does this user have access, and what role".

    Never trust a role or list_id supplied by the client — always re-derive it here from
    the list's owner_id and the list_members table.
    """
    if shopping_list.owner_id == user_id:
        return ListRole.OWNER

    result = await db.execute(
        select(ListMember).where(
            ListMember.list_id == shopping_list.id,
            ListMember.user_id == user_id,
            ListMember.status == MemberStatus.ACTIVE,
        )
    )
    member = result.scalar_one_or_none()
    return member.role if member else None


async def require_role(
    db: AsyncSession, list_id: uuid.UUID, user_id: uuid.UUID, min_role: ListRole
) -> tuple[ShoppingList, ListRole]:
    shopping_list = await get_list_or_404(db, list_id)
    role = await resolve_role(db, shopping_list, user_id)
    if role is None or _ROLE_RANK[role] < _ROLE_RANK[min_role]:
        # 404 instead of 403: don't confirm the list exists to a non-member.
        raise NOT_FOUND
    return shopping_list, role
