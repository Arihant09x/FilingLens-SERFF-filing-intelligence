from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TimestampedModel


class AuditEvent(TimestampedModel):
	__tablename__ = "audit_events"

	user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
	document_id: Mapped[UUID | None] = mapped_column(ForeignKey("documents.id"), index=True, nullable=True)
	event_type: Mapped[str] = mapped_column(String(80), index=True)
	event_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
	ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
