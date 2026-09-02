import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.member import MemberInviteRequest, MemberOut
from app.schemas.invitation import InvitationOut
from app.services import invitations_service, members_service

router = APIRouter(tags=["members"])


@router.get("/lists/{list_id}/members", response_model=list[MemberOut])
async def get_members(
    list_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[MemberOut]:
    members = await members_service.list_members(db, list_id, user.id)
    return [MemberOut.model_validate(m) for m in members]


@router.post("/lists/{list_id}/members", response_model=InvitationOut, status_code=status.HTTP_201_CREATED)
async def invite_member(
    list_id: uuid.UUID,
    payload: MemberInviteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InvitationOut:
    invitation = await invitations_service.create_invitation(
        db, list_id, user.id, payload.email, payload.role
    )
    await db.commit()
    out = InvitationOut.model_validate(invitation)
    out.list_name = invitation.shopping_list.name if invitation.shopping_list else None
    return out


@router.delete("/lists/{list_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    list_id: uuid.UUID,
    user_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await members_service.remove_member(db, list_id, user.id, user_id)
    await db.commit()
