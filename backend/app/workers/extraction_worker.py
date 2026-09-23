from datetime import datetime, timezone
from uuid import UUID

from app.db.session import SessionLocal
from app.models.document import Document
from app.services.extraction_service import process_document
from app.core.logging import get_logger

logger = get_logger(__name__)


async def run_extraction_job(document_id: UUID, request_id: str | None = None, job_id: str | None = None) -> None:
	if isinstance(document_id, str):
		document_id = UUID(document_id)
	async with SessionLocal() as db:
		document = await db.get(Document, document_id)
		if document is None:
			return
		job_id = job_id or str(document_id)
		document.job_id = job_id
		document.status = "processing"
		document.stage = "opening_pdf"
		document.message = "Opening PDF"
		document.started_at = datetime.now(timezone.utc)
		document.last_progress_at = document.started_at
		document.error_message = None
		document.progress_percentage = 5
		await db.commit()
		try:
			await process_document(db, document, job_id=job_id, request_id=request_id)
		except Exception:
			document.status = "failed"
			document.stage = "failed"
			document.message = "Extraction failed"
			document.error_message = "Unable to process PDF"
			document.last_progress_at = datetime.now(timezone.utc)
			await db.commit()
			logger.exception("extraction_job_failed", document_id=str(document.id), job_id=job_id, request_id=request_id)
			raise


async def worker_loop() -> None:
	from app.workers.queue import queue

	logger.info("worker_started")
	while True:
		job = await queue.dequeue(timeout=5)
		if job is None:
			continue
		try:
			await run_extraction_job(UUID(job["document_id"]), request_id=job.get("request_id"), job_id=job.get("job_id"))
		except Exception:
			continue


if __name__ == "__main__":
	import asyncio
	asyncio.run(worker_loop())
