import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.invitation import Invitation
from app.models.user import User
from app.schemas.invitation import InvitationOut
from app.services import invitations_service

router = APIRouter(prefix="/invitations", tags=["invitations"])


def _to_out(invitation: Invitation) -> InvitationOut:
    out = InvitationOut.model_validate(invitation)
    out.list_name = invitation.shopping_list.name if invitation.shopping_list else None
    return out


@router.get("", response_model=list[InvitationOut])
async def get_invitations(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> list[InvitationOut]:
    invitations = await invitations_service.list_pending_invitations(db, user.id)
    return [_to_out(i) for i in invitations]


@router.post("/{invitation_id}/accept", response_model=InvitationOut)
async def accept_invitation(
    invitation_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    await invitations_service.accept_invitation(db, invitation_id, user.id)
    await db.commit()
    invitation = await db.get(
        Invitation, invitation_id, options=[selectinload(Invitation.sender), selectinload(Invitation.shopping_list)]
    )
    return _to_out(invitation)


@router.post("/{invitation_id}/reject", status_code=204)
async def reject_invitation(
    invitation_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> None:
    await invitations_service.reject_invitation(db, invitation_id, user.id)
    await db.commit()
