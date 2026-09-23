from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import create_token, hash_password, verify_password
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)


async def register(db: AsyncSession, email: str, password: str) -> User:
	existing = await db.scalar(select(User).where(User.email == email.lower()))
	if existing:
		raise ValueError("An account with this email already exists")
	user = User(email=email.lower(), hashed_password=hash_password(password))
	db.add(user)
	await db.commit()
	await db.refresh(user)
	logger.info("user_registered", user_id=str(user.id))
	return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
	user = await db.scalar(select(User).where(User.email == email.lower()))
	if user and verify_password(password, user.hashed_password):
		logger.info("user_login_success", user_id=str(user.id))
		return user
	logger.warning("user_login_failed")
	return None


def tokens_for(user: User) -> dict[str, str]:
	settings = get_settings()
	return {
		"access_token": create_token(user.id, "access", timedelta(minutes=settings.jwt_access_expire_minutes)),
		"refresh_token": create_token(user.id, "refresh", timedelta(days=settings.jwt_refresh_expire_days)),
		"token_type": "bearer",
	}
