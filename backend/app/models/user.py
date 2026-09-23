from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import TimestampedModel


class User(TimestampedModel):
	__tablename__ = "users"

	email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
	hashed_password: Mapped[str] = mapped_column(String(255))
	is_active: Mapped[bool] = mapped_column(Boolean, default=True)
