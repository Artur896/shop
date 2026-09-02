import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.item import ItemCreate, ItemOut
from app.schemas.list import ListCreate, ListSummary, ListUpdate
from app.services import items_service, lists_service
from app.services.authz import require_role
from app.models.enums import ListRole
from sqlalchemy import select
from app.models.item import ShoppingItem

router = APIRouter(tags=["lists"])


@router.get("/lists")
async def get_lists(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> dict[str, list[ListSummary]]:
    mine, shared = await lists_service.list_my_lists(db, user.id)
    return {"mine": mine, "shared": shared}


@router.post("/lists", response_model=ListSummary, status_code=status.HTTP_201_CREATED)
async def create_list(
    payload: ListCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ListSummary:
    shopping_list = await lists_service.create_list(db, user.id, payload)
    await db.commit()
    return await lists_service.get_list_detail(db, shopping_list.id, user.id)


@router.get("/lists/{list_id}", response_model=ListSummary)
async def get_list(
    list_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> ListSummary:
    return await lists_service.get_list_detail(db, list_id, user.id)


@router.patch("/lists/{list_id}", response_model=ListSummary)
async def update_list(
    list_id: uuid.UUID,
    payload: ListUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ListSummary:
    await lists_service.update_list(db, list_id, user.id, payload)
    await db.commit()
    return await lists_service.get_list_detail(db, list_id, user.id)


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    await lists_service.delete_list(db, list_id, user.id)
    await db.commit()


@router.get("/lists/{list_id}/items", response_model=list[ItemOut])
async def get_items(
    list_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[ItemOut]:
    await require_role(db, list_id, user.id, ListRole.VIEWER)
    result = await db.execute(
        select(ShoppingItem).where(ShoppingItem.list_id == list_id).order_by(ShoppingItem.created_at.asc())
    )
    return list(result.scalars().all())


@router.post("/lists/{list_id}/items", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def add_item(
    list_id: uuid.UUID,
    payload: ItemCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemOut:
    item = await items_service.add_item(db, list_id, user.id, payload)
    await db.commit()
    return item
