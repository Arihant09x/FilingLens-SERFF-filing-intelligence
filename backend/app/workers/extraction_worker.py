from uuid import UUID

from app.db.session import SessionLocal
from app.models.document import Document
from app.services.extraction_service import process_document


async def run_extraction_job(document_id: UUID, request_id: str | None = None) -> None:
	async with SessionLocal() as db:
		document = await db.get(Document, document_id)
		if document is None:
			return
		try:
			await process_document(db, document, job_id=str(document_id), request_id=request_id)
		except Exception:
			document.status = "failed"
			await db.commit()
			raise
