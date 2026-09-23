from typing import Annotated
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.document import Document
from app.models.extraction_version import ExtractionVersion
from app.models.user import User
from app.schemas.document import DocumentResponse, UploadResponse
from app.services.document_service import create_document
from app.utils.file_validation import validate_pdf
from app.workers.queue import queue
from app.storage.local import LocalStorage
from app.core.config import get_settings
from app.core.logging import get_logger

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
storage = LocalStorage()
logger = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(request: Request, file: Annotated[UploadFile, File(...)], user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	content = await file.read()
	try:
		validate_pdf(file.filename or "upload.pdf", content)
		document = await create_document(db, user.id, file.filename or "upload.pdf", content)
	except ValueError as error:
		raise HTTPException(status_code=422, detail=str(error))
	document.status = "queued"
	document.stage = "queued"
	document.progress_percentage = 0
	document.current_page = 0
	document.total_pages = None
	document.message = "Queued for processing"
	await db.commit()
	job_id = await queue.enqueue(str(document.id), request_id=getattr(request.state, "request_id", None))
	document.job_id = job_id
	await db.commit()
	logger.info("extraction_job_queued", document_id=str(document.id), job_id=job_id)
	return {"document_id": document.id, "job_id": job_id, "status": document.status}


@router.get("", response_model=list[DocumentResponse])
async def list_documents(user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	return list((await db.scalars(select(Document).where(Document.user_id == user.id).order_by(Document.created_at.desc()))).all())


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	document = await db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
	if document is None:
		raise HTTPException(status_code=404, detail="Document not found")
	return document


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	document = await db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
	if document is None:
		raise HTTPException(status_code=404, detail="Document not found")
	await storage.delete(document.storage_key)
	await db.delete(document)
	await db.commit()
	logger.info("document_deleted", user_id=str(user.id), document_id=str(document_id))


@router.post("/{document_id}/extract")
async def extract(document_id: UUID, request: Request, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	document = await db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
	if document is None:
		raise HTTPException(status_code=404, detail="Document not found")
	stale_after = timedelta(minutes=get_settings().processing_stale_minutes)
	last_activity = document.last_progress_at or document.started_at or document.created_at
	if document.status == "queued":
		return {"document_id": document.id, "job_id": document.job_id or str(document.id), "status": document.status}
	if document.status == "processing" and datetime.now(timezone.utc) - last_activity < stale_after:
		return {"document_id": document.id, "job_id": document.job_id or str(document.id), "status": document.status}
	document.status = "queued"
	document.stage = "queued"
	document.message = "Queued for processing"
	document.progress_percentage = 0
	document.current_page = 0
	document.total_pages = None
	document.started_at = None
	document.completed_at = None
	document.error_message = None
	await db.commit()
	job_id = await queue.enqueue(str(document.id), request_id=getattr(request.state, "request_id", None))
	document.job_id = job_id
	await db.commit()
	return {"document_id": document.id, "job_id": job_id, "status": document.status}


@router.get("/{document_id}/extractions")
async def list_extractions(document_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	await get_document(document_id, user, db)
	return list((await db.scalars(select(ExtractionVersion).where(ExtractionVersion.document_id == document_id).order_by(ExtractionVersion.version.desc()))).all())


@router.get("/{document_id}/extractions/{version}")
async def get_extraction(document_id: UUID, version: int, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	await get_document(document_id, user, db)
	result = await db.scalar(select(ExtractionVersion).where(ExtractionVersion.document_id == document_id, ExtractionVersion.version == version))
	if result is None:
		raise HTTPException(status_code=404, detail="Extraction version not found")
	return result


@router.get("/{document_id}/review")
async def review(document_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	await get_document(document_id, user, db)
	result = await db.scalar(select(ExtractionVersion).where(ExtractionVersion.document_id == document_id).order_by(ExtractionVersion.version.desc()))
	return {"flags": result.structured_data.get("review_flags", []) if result else []}
