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
	document = Document(id=document_id, user_id=user_id, filename=filename, storage_key=key, file_size=len(content), sha256=sha256(content).hexdigest(), status="queued", stage="queued", progress_percentage=0, current_page=0)
	db.add(document)
	await db.commit()
	await db.refresh(document)
	logger.info("document_uploaded", user_id=str(user_id), document_id=str(document.id), file_size=document.file_size)
	return document


async def extract_document(db: AsyncSession, document: Document, *, data: dict | None = None) -> ExtractionVersion:
	document.status = "processing"
	document.stage = "persisting"
	document.message = "Saving extracted data"
	document.progress_percentage = 85
	await db.commit()
	if data is None:
		content = await storage.read(document.storage_key)
		import tempfile
		from pathlib import Path
		with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
			temp_file.write(content)
			path = Path(temp_file.name)
		try:
			data = run_extraction(path)
		finally:
			if path.exists():
				path.unlink(missing_ok=True)
	document.page_count = data["snapshot"]["page_count"]
	document.total_pages = document.page_count
	version_number = (await db.scalar(select(ExtractionVersion.version).where(ExtractionVersion.document_id == document.id).order_by(ExtractionVersion.version.desc()).limit(1)) or 0) + 1
	version = ExtractionVersion(document_id=document.id, version=version_number, strategy="default", status="completed", structured_data=data, confidence_summary=data["snapshot"])
	db.add(version)
	await db.commit()
	await db.refresh(version)
	return version
