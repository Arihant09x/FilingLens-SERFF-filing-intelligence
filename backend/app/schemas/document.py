from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
	id: UUID
	filename: str
	file_size: int
	page_count: int | None
	status: str
	current_page: int
	total_pages: int | None
	progress_percentage: float
	created_at: datetime

	model_config = {"from_attributes": True}


class UploadResponse(BaseModel):
	document_id: UUID
	job_id: str
	status: str
