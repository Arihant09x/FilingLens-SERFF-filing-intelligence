from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.extraction_version import ExtractionVersion


async def latest(db: AsyncSession, document_id: UUID) -> ExtractionVersion | None:
	return await db.scalar(select(ExtractionVersion).where(ExtractionVersion.document_id == document_id).order_by(ExtractionVersion.version.desc()))


async def list_versions(db: AsyncSession, document_id: UUID) -> list[ExtractionVersion]:
	return list((await db.scalars(select(ExtractionVersion).where(ExtractionVersion.document_id == document_id).order_by(ExtractionVersion.version.desc()))).all())


async def next_version(db: AsyncSession, document_id: UUID) -> int:
	current = await db.scalar(select(ExtractionVersion.version).where(ExtractionVersion.document_id == document_id).order_by(ExtractionVersion.version.desc()).limit(1))
	return (current or 0) + 1
