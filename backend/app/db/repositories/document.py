from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


async def get_owned(db: AsyncSession, document_id: UUID, user_id: UUID) -> Document | None:
	return await db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user_id))


async def list_owned(db: AsyncSession, user_id: UUID) -> list[Document]:
	return list((await db.scalars(select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc()))).all())


async def save(db: AsyncSession, document: Document) -> Document:
	db.add(document)
	await db.commit()
	await db.refresh(document)
	return document
