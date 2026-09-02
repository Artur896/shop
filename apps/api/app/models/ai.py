import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import AIIntegrationStatus, AIProvider


class AIIntegration(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "ai_integrations"
    __table_args__ = (UniqueConstraint("user_id", "provider", name="uq_user_provider"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[AIProvider] = mapped_column(Enum(AIProvider, name="ai_provider"), nullable=False)
    status: Mapped[AIIntegrationStatus] = mapped_column(
        Enum(AIIntegrationStatus, name="ai_integration_status"),
        default=AIIntegrationStatus.DISCONNECTED,
        nullable=False,
    )
    granted_scopes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    tokens = relationship("AIToken", back_populates="integration", cascade="all, delete-orphan")


class AIToken(UUIDMixin, Base):
    __tablename__ = "ai_tokens"

    integration_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ai_integrations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    scopes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    integration = relationship("AIIntegration", back_populates="tokens")
