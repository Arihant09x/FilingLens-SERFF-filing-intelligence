from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Request, UploadFile
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
from app.workers.extraction_worker import run_extraction_job
from app.storage.local import LocalStorage
from app.core.logging import get_logger

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])
storage = LocalStorage()
logger = get_logger(__name__)


@router.post("/upload", response_model=UploadResponse, status_code=201)
async def upload_document(background_tasks: BackgroundTasks, request: Request, file: Annotated[UploadFile, File(...)], user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	content = await file.read()
	try:
		validate_pdf(file.filename or "upload.pdf", content)
		document = await create_document(db, user.id, file.filename or "upload.pdf", content)
	except ValueError as error:
		raise HTTPException(status_code=422, detail=str(error))
	document.status = "queued"
	await db.commit()
	background_tasks.add_task(run_extraction_job, document.id, request.state.request_id)
	return {"document_id": document.id, "job_id": str(document.id), "status": document.status}


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
async def extract(document_id: UUID, background_tasks: BackgroundTasks, request: Request, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	document = await db.scalar(select(Document).where(Document.id == document_id, Document.user_id == user.id))
	if document is None:
		raise HTTPException(status_code=404, detail="Document not found")
	document.status = "queued"
	await db.commit()
	background_tasks.add_task(run_extraction_job, document.id, request.state.request_id)
	return {"document_id": document.id, "job_id": str(document.id), "status": document.status}


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
