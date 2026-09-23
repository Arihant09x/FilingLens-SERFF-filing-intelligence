from typing import Any

from pydantic import BaseModel


class ReviewFlagsResponse(BaseModel):
	flags: list[dict[str, Any]]
