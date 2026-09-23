from io import BytesIO
from time import perf_counter
from uuid import UUID
import asyncio

import pdfplumber
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.extraction.pipeline import run_extraction
from app.models.document import Document
from app.services.document_service import extract_document
from app.storage.base import get_storage

logger = get_logger(__name__)


async def _update_progress(db: AsyncSession, document: Document, *, percentage: float, stage: str, current_page: int | None = None, total_pages: int | None = None, message: str | None = None, status: str | None = None) -> None:
	if current_page is not None:
		document.current_page = current_page
	if total_pages is not None:
		document.total_pages = total_pages
	if status is not None:
		document.status = status
	document.stage = stage
	document.message = message or stage
	document.progress_percentage = max(0, min(100, percentage))
	document.last_progress_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
	await db.commit()


async def process_document(db: AsyncSession, document: Document, *, job_id: str | None = None, request_id: str | None = None):
	"""Process one queued document with realistic page-based progress."""
	started = perf_counter()
	job_id = job_id or str(document.id)
	request_id = request_id or f"job-{job_id}"
	storage = get_storage()
	logger.info("extraction_started", request_id=request_id, user_id=str(document.user_id), document_id=str(document.id), job_id=job_id, status="processing")
	document.status = "processing"
	document.stage = "opening_pdf"
	document.message = "Opening PDF"
	document.progress_percentage = 5
	document.last_progress_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
	await db.commit()
	try:
		content = await storage.read(document.storage_key)
		with pdfplumber.open(BytesIO(content)) as pdf:
			page_count = len(pdf.pages)
			document.page_count = page_count
			document.total_pages = page_count
			document.current_page = 0
			document.message = "PDF ready"
			await db.commit()
			logger.info("page_count_detected", document_id=str(document.id), job_id=job_id, page_count=page_count)
			for page_number, page in enumerate(pdf.pages, start=1):
				page.extract_text() or ""
				document.current_page = page_number
				document.stage = "extracting_pages"
				document.message = f"Extracting page {page_number} of {page_count}"
				document.progress_percentage = max(10, min(70, 10 + (page_number / page_count) * 60)) if page_count else 10
				document.last_progress_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
				await db.commit()
				logger.info("page_completed", document_id=str(document.id), job_id=job_id, current_page=page_number, total_pages=page_count, progress=document.progress_percentage)
		if page_count:
			document.progress_percentage = 70
			document.stage = "analyzing_serff"
			document.message = "Analyzing SERFF structure"
			document.last_progress_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
			await db.commit()
		import tempfile
		from pathlib import Path
		with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
			temp_file.write(content)
			temp_path = Path(temp_file.name)
		try:
			data = await asyncio.to_thread(run_extraction, temp_path)
		finally:
			if temp_path.exists():
				temp_path.unlink(missing_ok=True)
		version = await extract_document(db, document, data=data)
		document.current_page = document.page_count or 0
		document.total_pages = document.page_count
		document.progress_percentage = 100
		document.stage = "completed"
		document.message = "Completed"
		document.status = "completed"
		document.completed_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
		document.last_progress_at = document.completed_at
		await db.commit()
	except Exception:
		duration_ms = round((perf_counter() - started) * 1000, 2)
		document.status = "failed"
		document.stage = "failed"
		document.error_message = "Unable to process PDF"
		document.message = "Extraction failed"
		document.last_progress_at = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
		await db.commit()
		logger.exception("extraction_failed", request_id=request_id, user_id=str(document.user_id), document_id=str(document.id), job_id=job_id, page_count=document.page_count, duration_ms=duration_ms, status="failed")
		raise
	duration_ms = round((perf_counter() - started) * 1000, 2)
	logger.info("extraction_completed", request_id=request_id, user_id=str(document.user_id), document_id=str(document.id), job_id=job_id, page_count=document.page_count, duration_ms=duration_ms, status="completed")
	return version
