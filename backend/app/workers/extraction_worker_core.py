# backend/app/workers/extraction_worker_core.py
import asyncio
from datetime import datetime, timezone
from uuid import UUID

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.models.document import Document
from app.services.extraction_service import process_document
from app.workers.queue import queue

logger = get_logger(__name__)


async def run_extraction_job(
    document_id: UUID,
    request_id: str | None = None,
    job_id: str | None = None,
) -> None:
    if isinstance(document_id, str):
        document_id = UUID(document_id)

    async with SessionLocal() as db:
        document = await db.get(Document, document_id)
        if document is None:
            logger.warning(
                "extraction_skipped_document_missing",
                document_id=str(document_id),
                job_id=job_id,
                request_id=request_id,
            )
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

        logger.info(
            "extraction_started",
            document_id=str(document.id),
            job_id=job_id,
            request_id=request_id,
            filename=document.filename,
        )

        try:
            await process_document(db, document, job_id=job_id, request_id=request_id)
            logger.info(
                "extraction_completed",
                document_id=str(document.id),
                job_id=job_id,
                request_id=request_id,
                page_count=document.page_count,
                progress=document.progress_percentage,
            )
        except Exception as exc:
            document.status = "failed"
            document.stage = "failed"
            document.message = "Extraction failed"
            # Capture the real error so the frontend can display it
            document.error_message = f"{type(exc).__name__}: {exc}"[:1000]
            document.last_progress_at = datetime.now(timezone.utc)
            await db.commit()
            logger.exception(
                "extraction_job_failed",
                document_id=str(document.id),
                job_id=job_id,
                request_id=request_id,
                error=str(exc),
                error_type=type(exc).__name__,
            )
            raise


async def worker_loop() -> None:
    logger.info("worker_started", queue="extraction_jobs")

    while True:
        try:
            job = await queue.dequeue(timeout=5)
        except Exception:
            logger.warning("worker_dequeue_backoff")
            await asyncio.sleep(2)
            continue

        if job is None:
            continue

        document_id = job.get("document_id")
        job_id = job.get("job_id")
        request_id = job.get("request_id")

        if not document_id:
            logger.error("job_missing_document_id", raw=job)
            continue

        try:
            await run_extraction_job(
                UUID(document_id),
                request_id=request_id,
                job_id=job_id,
            )
        except Exception:
            logger.error(
                "worker_job_aborted",
                document_id=document_id,
                job_id=job_id,
            )
            continue


def main() -> None:
    """Entry point for `python -m app.workers.extraction_worker_core`."""
    asyncio.run(worker_loop())


if __name__ == "__main__":
    main()