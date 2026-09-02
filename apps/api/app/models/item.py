import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class ShoppingItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "shopping_items"

    list_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("shopping_lists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(10, 2), default=1, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(30), nullable=True)
    category: Mapped[str] = mapped_column(String(50), default="otros", nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    shopping_list = relationship("ShoppingList", back_populates="items")
