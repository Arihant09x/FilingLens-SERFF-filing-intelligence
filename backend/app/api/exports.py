from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.extraction_version import ExtractionVersion
from app.models.user import User
from app.services.export_service import as_csv, as_json, as_markdown
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["exports"])


async def latest(document_id: UUID, user: User, db: AsyncSession) -> dict:
	document = await db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
	if document is None:
		raise HTTPException(status_code=404, detail="Document not found")
	version = await db.scalar(select(ExtractionVersion).where(ExtractionVersion.document_id == document_id).order_by(ExtractionVersion.version.desc()))
	if version is None:
		raise HTTPException(status_code=404, detail="No extraction available")
	return version.structured_data


@router.get("/{document_id}/export/json")
async def export_json(document_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	result = PlainTextResponse(as_json(await latest(document_id, user, db)), media_type="application/json", headers={"Content-Disposition": "attachment; filename=filing.json"})
	logger.info("export_generated", user_id=str(user.id), document_id=str(document_id), format="json")
	return result


@router.get("/{document_id}/export/csv")
async def export_csv(document_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	result = PlainTextResponse(as_csv(await latest(document_id, user, db)), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=filing.csv"})
	logger.info("export_generated", user_id=str(user.id), document_id=str(document_id), format="csv")
	return result


@router.get("/{document_id}/export/markdown")
async def export_markdown(document_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	result = PlainTextResponse(as_markdown(await latest(document_id, user, db)), media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=filing.md"})
	logger.info("export_generated", user_id=str(user.id), document_id=str(document_id), format="markdown")
	return result
