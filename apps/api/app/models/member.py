import uuid

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import ListRole, MemberStatus


class ListMember(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "list_members"
    __table_args__ = (UniqueConstraint("list_id", "user_id", name="uq_list_member"),)

    list_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[ListRole] = mapped_column(Enum(ListRole, name="list_role"), nullable=False)
    status: Mapped[MemberStatus] = mapped_column(
        Enum(MemberStatus, name="member_status"), default=MemberStatus.ACTIVE, nullable=False
    )

    shopping_list = relationship("ShoppingList", back_populates="members")
    user = relationship("User")
