import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.item import ItemOut, ItemUpdate
from app.services import items_service

router = APIRouter(prefix="/items", tags=["items"])


@router.patch("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: uuid.UUID,
    payload: ItemUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemOut:
    item = await items_service.update_item(db, item_id, user.id, payload)
    await db.commit()
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    await items_service.delete_item(db, item_id, user.id)
    await db.commit()


@router.post("/{item_id}/complete", response_model=ItemOut)
async def complete_item(
    item_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ItemOut:
    item = await items_service.update_item(db, item_id, user.id, ItemUpdate(is_completed=True))
    await db.commit()
    return item


@router.post("/{item_id}/uncomplete", response_model=ItemOut)
async def uncomplete_item(
    item_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ItemOut:
    item = await items_service.update_item(db, item_id, user.id, ItemUpdate(is_completed=False))
    await db.commit()
    return item
