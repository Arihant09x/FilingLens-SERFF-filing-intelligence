from hashlib import sha256
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.extraction_version import ExtractionVersion
from app.storage.base import safe_key
from app.storage.base import get_storage
from app.extraction.pipeline import run_extraction
from app.core.logging import get_logger

logger = get_logger(__name__)

storage = get_storage()


async def create_document(db: AsyncSession, user_id: UUID, filename: str, content: bytes) -> Document:
	document_id = uuid4()
	key = safe_key(str(document_id), filename)
	await storage.save(key, content)
	document = Document(id=document_id, user_id=user_id, filename=filename, storage_key=key, file_size=len(content), sha256=sha256(content).hexdigest(), status="uploaded")
	db.add(document)
	await db.commit()
	await db.refresh(document)
	logger.info("document_uploaded", user_id=str(user_id), document_id=str(document.id), file_size=document.file_size)
	return document


async def extract_document(db: AsyncSession, document: Document) -> ExtractionVersion:
	document.status = "processing"
	await db.commit()
	path = storage.root / document.storage_key
	data = run_extraction(path)
	document.page_count = data["snapshot"]["page_count"]
	document.status = "completed"
	version_number = (await db.scalar(select(ExtractionVersion.version).where(ExtractionVersion.document_id == document.id).order_by(ExtractionVersion.version.desc()).limit(1)) or 0) + 1
	version = ExtractionVersion(document_id=document.id, version=version_number, strategy="default", status="completed", structured_data=data, confidence_summary=data["snapshot"])
	db.add(version)
	await db.commit()
	await db.refresh(version)
	return version
