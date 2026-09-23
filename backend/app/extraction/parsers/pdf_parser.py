from pathlib import Path
from typing import Any

import pdfplumber


def parse_pdf(path: str | Path) -> dict[str, Any]:
	"""Extract layout-aware words and tables while preserving page evidence."""
	pages: list[dict[str, Any]] = []
	with pdfplumber.open(path) as pdf:
		for page_number, page in enumerate(pdf.pages, start=1):
			words = page.extract_words(extra_attrs=["fontname", "size"], keep_blank_chars=False)
			tables = []
			for table in page.find_tables():
				tables.append({"rows": table.extract(), "bbox": list(table.bbox), "page": page_number})
			pages.append({
				"page": page_number,
				"width": page.width,
				"height": page.height,
				"text": page.extract_text() or "",
				"words": words,
				"tables": tables,
			})
	return {"page_count": len(pages), "pages": pages}
