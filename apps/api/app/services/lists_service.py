import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ListRole, MemberStatus
from app.models.item import ShoppingItem
from app.models.list import ShoppingList
from app.models.member import ListMember
from app.schemas.list import ListCreate, ListSummary, ListUpdate
from app.services.authz import require_role


async def create_list(db: AsyncSession, owner_id: uuid.UUID, data: ListCreate) -> ShoppingList:
    shopping_list = ShoppingList(
        owner_id=owner_id, name=data.name, description=data.description, icon=data.icon
    )
    db.add(shopping_list)
    await db.flush()
    return shopping_list


async def _to_summary(db: AsyncSession, shopping_list: ShoppingList, user_id: uuid.UUID) -> ListSummary:
    counts = await db.execute(
        select(
            func.count(ShoppingItem.id),
            func.count(ShoppingItem.id).filter(ShoppingItem.is_completed.is_(True)),
        ).where(ShoppingItem.list_id == shopping_list.id)
    )
    total, completed = counts.one()
    role = ListRole.OWNER
    if shopping_list.owner_id != user_id:
        member_result = await db.execute(
            select(ListMember).where(
                ListMember.list_id == shopping_list.id, ListMember.user_id == user_id
            )
        )
        member = member_result.scalar_one_or_none()
        role = member.role if member else ListRole.VIEWER

    return ListSummary(
        id=shopping_list.id,
        name=shopping_list.name,
        description=shopping_list.description,
        icon=shopping_list.icon,
        owner_id=shopping_list.owner_id,
        version=shopping_list.version,
        created_at=shopping_list.created_at,
        updated_at=shopping_list.updated_at,
        total_items=total or 0,
        completed_items=completed or 0,
        my_role=role,
    )


async def list_my_lists(db: AsyncSession, user_id: uuid.UUID) -> tuple[list[ListSummary], list[ListSummary]]:
    owned_result = await db.execute(
        select(ShoppingList)
        .where(ShoppingList.owner_id == user_id)
        .order_by(ShoppingList.updated_at.desc())
    )
    owned = owned_result.scalars().all()

    shared_result = await db.execute(
        select(ShoppingList)
        .join(ListMember, ListMember.list_id == ShoppingList.id)
        .where(ListMember.user_id == user_id, ListMember.status == MemberStatus.ACTIVE)
        .order_by(ShoppingList.updated_at.desc())
    )
    shared = shared_result.scalars().all()

    mine = [await _to_summary(db, sl, user_id) for sl in owned]
    shared_with_me = [await _to_summary(db, sl, user_id) for sl in shared]
    return mine, shared_with_me


async def get_list_detail(db: AsyncSession, list_id: uuid.UUID, user_id: uuid.UUID) -> ListSummary:
    shopping_list, _ = await require_role(db, list_id, user_id, ListRole.VIEWER)
    return await _to_summary(db, shopping_list, user_id)


async def get_list_for_role(db: AsyncSession, list_id: uuid.UUID, user_id: uuid.UUID, min_role: ListRole):
    return await require_role(db, list_id, user_id, min_role)


async def update_list(
    db: AsyncSession, list_id: uuid.UUID, user_id: uuid.UUID, data: ListUpdate
) -> ShoppingList:
    shopping_list, _ = await require_role(db, list_id, user_id, ListRole.OWNER)
    if data.name is not None:
        shopping_list.name = data.name
    if data.description is not None:
        shopping_list.description = data.description
    if data.icon is not None:
        shopping_list.icon = data.icon
    shopping_list.version += 1
    await db.flush()
    return shopping_list


async def delete_list(db: AsyncSession, list_id: uuid.UUID, user_id: uuid.UUID) -> None:
    shopping_list, _ = await require_role(db, list_id, user_id, ListRole.OWNER)
    await db.delete(shopping_list)
    await db.flush()


async def find_lists_by_name(db: AsyncSession, user_id: uuid.UUID, name: str) -> list[ShoppingList]:
    """Used by the AI layer to resolve a list by name and detect ambiguity
    (e.g. two lists both called "Casa") instead of guessing which one to modify."""
    owned_result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.owner_id == user_id, func.lower(ShoppingList.name) == name.lower()
        )
    )
    shared_result = await db.execute(
        select(ShoppingList)
        .join(ListMember, ListMember.list_id == ShoppingList.id)
        .where(
            ListMember.user_id == user_id,
            ListMember.status == MemberStatus.ACTIVE,
            func.lower(ShoppingList.name) == name.lower(),
        )
    )
    seen: dict[uuid.UUID, ShoppingList] = {}
    for sl in [*owned_result.scalars().all(), *shared_result.scalars().all()]:
        seen[sl.id] = sl
    return list(seen.values())
