import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    # Without this, an UPDATE that only touches an `onupdate=func.now()` column (no
    # other tracked change fetched via RETURNING) leaves the ORM instance holding the
    # stale in-memory `updated_at` — reading it later doesn't error, it's just wrong.
    # Worse, under asyncio a *subsequent* implicit refresh of it can hit MissingGreenlet
    # since lazy IO outside an awaited call isn't valid on an AsyncSession. Fetching
    # server-generated defaults eagerly on every flush avoids both failure modes.
    __mapper_args__ = {"eager_defaults": True}


class UUIDMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
