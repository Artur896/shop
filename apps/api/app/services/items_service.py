import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ListRole
from app.models.item import ShoppingItem
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate
from app.services.authz import require_role
from app.ws.redis_pubsub import publish_list_event

ITEM_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")


async def get_item_or_404(db: AsyncSession, item_id: uuid.UUID) -> ShoppingItem:
    item = await db.get(ShoppingItem, item_id)
    if item is None:
        raise ITEM_NOT_FOUND
    return item


async def add_item(
    db: AsyncSession, list_id: uuid.UUID, user_id: uuid.UUID, data: ItemCreate
) -> ShoppingItem:
    await require_role(db, list_id, user_id, ListRole.EDITOR)
    item = ShoppingItem(
        list_id=list_id,
        name=data.name,
        quantity=data.quantity,
        unit=data.unit,
        category=data.category,
        notes=data.notes,
        estimated_price=data.estimated_price,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    await publish_list_event(list_id, "ITEM_CREATED", ItemOut.model_validate(item).model_dump(mode="json"))
    return item


async def update_item(
    db: AsyncSession, item_id: uuid.UUID, user_id: uuid.UUID, data: ItemUpdate
) -> ShoppingItem:
    item = await get_item_or_404(db, item_id)
    await require_role(db, item.list_id, user_id, ListRole.EDITOR)

    was_completed = item.is_completed
    if data.name is not None:
        item.name = data.name
    if data.quantity is not None:
        item.quantity = data.quantity
    if data.unit is not None:
        item.unit = data.unit
    if data.category is not None:
        item.category = data.category
    if data.notes is not None:
        item.notes = data.notes
    if data.estimated_price is not None:
        item.estimated_price = data.estimated_price
    if data.is_completed is not None:
        item.is_completed = data.is_completed

    # Last-Write-Wins: we don't reject stale `version` values, we just always apply the
    # newest write and bump the counter so clients can detect they raced someone else.
    item.version += 1
    await db.flush()
    await db.refresh(item)

    event = "ITEM_UPDATED"
    if data.is_completed is not None and data.is_completed != was_completed:
        event = "ITEM_COMPLETED" if data.is_completed else "ITEM_UNCOMPLETED"
    await publish_list_event(item.list_id, event, ItemOut.model_validate(item).model_dump(mode="json"))
    return item


async def delete_item(db: AsyncSession, item_id: uuid.UUID, user_id: uuid.UUID) -> None:
    item = await get_item_or_404(db, item_id)
    await require_role(db, item.list_id, user_id, ListRole.EDITOR)
    list_id, deleted_id = item.list_id, item.id
    await db.delete(item)
    await db.flush()
    await publish_list_event(list_id, "ITEM_DELETED", {"id": str(deleted_id)})
