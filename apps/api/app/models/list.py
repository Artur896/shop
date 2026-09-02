import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ShoppingList(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "shopping_lists"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    owner = relationship("User", back_populates="owned_lists")
    items = relationship("ShoppingItem", back_populates="shopping_list", cascade="all, delete-orphan")
    members = relationship("ListMember", back_populates="shopping_list", cascade="all, delete-orphan")
