from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TimestampedModel


class ExtractionVersion(TimestampedModel):
	__tablename__ = "extraction_versions"

	document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"), index=True)
	version: Mapped[int] = mapped_column(Integer)
	strategy: Mapped[str] = mapped_column(String(64), default="default")
	status: Mapped[str] = mapped_column(String(32), default="completed")
	structured_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
	confidence_summary: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
