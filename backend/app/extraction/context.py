from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExtractionContext:
	pages: list[dict[str, Any]]
	sections: list[dict[str, Any]] = field(default_factory=list)
	tables: list[dict[str, Any]] = field(default_factory=list)
	attachments: list[dict[str, Any]] = field(default_factory=list)
	correspondence: list[dict[str, Any]] = field(default_factory=list)
	metadata: dict[str, Any] = field(default_factory=dict)

	@property
	def page_count(self) -> int:
		return len(self.pages)
