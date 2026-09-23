from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ExtractionRead(BaseModel):
	id: UUID
	document_id: UUID
	version: int
	strategy: str
	status: str
	structured_data: dict[str, Any]
	confidence_summary: dict[str, Any]

	model_config = {"from_attributes": True}
