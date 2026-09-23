from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
	id: UUID
	filename: str
	file_size: int
	page_count: int | None
	status: str
	stage: str | None = None
	message: str | None = None
	job_id: str | None = None
	current_page: int = 0
	total_pages: int | None = None
	progress_percentage: float = 0
	started_at: datetime | None = None
	completed_at: datetime | None = None
	last_progress_at: datetime | None = None
	error_message: str | None = None
	created_at: datetime

	model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
	document_id: UUID
	job_id: str
	status: str
