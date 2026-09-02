import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models.enums import InvitationStatus, ListRole, MemberStatus, NotificationType
from app.models.invitation import Invitation
from app.models.member import ListMember
from app.models.user import User
from app.services.authz import require_role
from app.services.notifications_service import notify
from app.ws.redis_pubsub import publish_list_event


async def create_invitation(
    db: AsyncSession,
    list_id: uuid.UUID,
    sender_id: uuid.UUID,
    receiver_email: str,
    role: ListRole,
) -> Invitation:
    shopping_list, _ = await require_role(db, list_id, sender_id, ListRole.OWNER)

    receiver_result = await db.execute(select(User).where(User.email == receiver_email.lower()))
    receiver = receiver_result.scalar_one_or_none()
    if receiver is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user with that email")
    if receiver.id == sender_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot invite yourself")

    existing_member = await db.execute(
        select(ListMember).where(
            ListMember.list_id == list_id,
            ListMember.user_id == receiver.id,
            ListMember.status == MemberStatus.ACTIVE,
        )
    )
    if existing_member.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member")

    invitation = Invitation(
        list_id=list_id,
        sender_id=sender_id,
        receiver_id=receiver.id,
        role=role,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.INVITATION_EXPIRE_DAYS),
    )
    # Populate the relationship directly from the object require_role() already
    # fetched, rather than leaving it to lazy-load later — under AsyncSession, an
    # un-awaited lazy load outside this function raises MissingGreenlet instead of
    # quietly querying, so this isn't just an optimization.
    invitation.shopping_list = shopping_list
    db.add(invitation)
    await db.flush()

    await notify(
        db,
        receiver.id,
        NotificationType.LIST_INVITATION,
        title="Nueva invitación",
        message=f'Te invitaron a "{shopping_list.name}"',
        data={"invitation_id": str(invitation.id), "list_id": str(list_id)},
    )
    return invitation


async def list_pending_invitations(db: AsyncSession, user_id: uuid.UUID) -> list[Invitation]:
    result = await db.execute(
        select(Invitation)
        .where(Invitation.receiver_id == user_id, Invitation.status == InvitationStatus.PENDING)
        .options(selectinload(Invitation.sender), selectinload(Invitation.shopping_list))
    )
    return list(result.scalars().all())


async def _get_own_invitation(db: AsyncSession, invitation_id: uuid.UUID, user_id: uuid.UUID) -> Invitation:
    invitation = await db.get(Invitation, invitation_id)
    if invitation is None or invitation.receiver_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")
    if invitation.status != InvitationStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Invitation already resolved")
    if invitation.expires_at < datetime.now(timezone.utc):
        invitation.status = InvitationStatus.EXPIRED
        await db.flush()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invitation expired")
    return invitation


async def accept_invitation(db: AsyncSession, invitation_id: uuid.UUID, user_id: uuid.UUID) -> ListMember:
    invitation = await _get_own_invitation(db, invitation_id, user_id)
    invitation.status = InvitationStatus.ACCEPTED

    member = ListMember(list_id=invitation.list_id, user_id=user_id, role=invitation.role)
    db.add(member)
    await db.flush()

    await notify(
        db,
        invitation.sender_id,
        NotificationType.INVITATION_ACCEPTED,
        title="Invitación aceptada",
        message="Aceptaron tu invitación a la lista",
        data={"list_id": str(invitation.list_id)},
    )
    await publish_list_event(
        invitation.list_id, "MEMBER_ADDED", {"user_id": str(user_id), "role": invitation.role.value}
    )
    return member


async def reject_invitation(db: AsyncSession, invitation_id: uuid.UUID, user_id: uuid.UUID) -> None:
    invitation = await _get_own_invitation(db, invitation_id, user_id)
    invitation.status = InvitationStatus.REJECTED
    await db.flush()
