from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_by_email(db: AsyncSession, email: str) -> User | None:
	return await db.scalar(select(User).where(User.email == email.lower()))


async def get_by_id(db: AsyncSession, user_id) -> User | None:
	return await db.get(User, user_id)


async def save(db: AsyncSession, user: User) -> User:
	db.add(user)
	await db.commit()
	await db.refresh(user)
	return user
