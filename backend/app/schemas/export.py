from typing import Literal

from pydantic import BaseModel


class ExportFormat(BaseModel):
	format: Literal["json", "csv", "markdown"]
