from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.services.document_service import extract_document
from app.core.logging import get_logger
from time import perf_counter

logger = get_logger(__name__)


async def process_document(db: AsyncSession, document: Document, *, job_id: str | None = None, request_id: str | None = None):
	"""Process one queued document; this function is the worker boundary."""
	started = perf_counter()
	job_id = job_id or str(document.id)
	request_id = request_id or f"job-{job_id}"
	logger.info("extraction_started", request_id=request_id, user_id=str(document.user_id), document_id=str(document.id), job_id=job_id, status="processing")
	document.status = "processing"
	document.progress_percentage = 10
	await db.commit()
	try:
		version = await extract_document(db, document)
		document.current_page = document.page_count or 0
		document.total_pages = document.page_count
		document.progress_percentage = 100
		await db.commit()
	except Exception:
		duration_ms = round((perf_counter() - started) * 1000, 2)
		logger.exception("extraction_failed", request_id=request_id, user_id=str(document.user_id), document_id=str(document.id), job_id=job_id, page_count=document.page_count, duration_ms=duration_ms, status="failed")
		raise
	duration_ms = round((perf_counter() - started) * 1000, 2)
	logger.info("extraction_completed", request_id=request_id, user_id=str(document.user_id), document_id=str(document.id), job_id=job_id, page_count=document.page_count, duration_ms=duration_ms, status="completed")
	return version
