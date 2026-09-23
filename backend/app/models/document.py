from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String
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
	current_page: Mapped[int] = mapped_column(Integer, default=0)
	total_pages: Mapped[int | None] = mapped_column(Integer)
	progress_percentage: Mapped[float] = mapped_column(Float, default=0)
