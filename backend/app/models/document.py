from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TimestampedModel


class Document(TimestampedModel):
	__tablename__ = "documents"

	user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
	filename: Mapped[str] = mapped_column(String(512))
	storage_key: Mapped[str] = mapped_column(String(512), unique=True)
	file_size: Mapped[int] = mapped_column(Integer)
	sha256: Mapped[str] = mapped_column(String(64), index=True)
	page_count: Mapped[int | None] = mapped_column(Integer)
	status: Mapped[str] = mapped_column(String(32), default="uploaded", index=True)
	stage: Mapped[str | None] = mapped_column(String(64), default="queued")
	message: Mapped[str | None] = mapped_column(String(255), default=None)
	job_id: Mapped[str | None] = mapped_column(String(128), default=None, index=True)
	attempt_count: Mapped[int] = mapped_column(Integer, default=0)
	current_page: Mapped[int] = mapped_column(Integer, default=0)
	total_pages: Mapped[int | None] = mapped_column(Integer)
	progress_percentage: Mapped[float] = mapped_column(Float, default=0)
	started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
	completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
	last_progress_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
	error_message: Mapped[str | None] = mapped_column(String(500), default=None)
