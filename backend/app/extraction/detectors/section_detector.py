from typing import Any


def build_sections(headings: list[dict[str, Any]], pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
	sections = []
	for index, heading in enumerate(headings):
		start_page = heading["page"]
		end_page = headings[index + 1]["page"] - 1 if index + 1 < len(headings) else len(pages)
		body_pages = [page for page in pages if start_page <= page["page"] <= end_page]
		sections.append({
			"heading": heading["text"], "level": heading.get("level", "H1"),
			"text": "\n".join(page.get("text", "") for page in body_pages),
			"section_type": heading["section_type"], "page_start": start_page,
			"page_end": end_page, "confidence": heading["confidence"], "source": heading["source"],
		})
	return sections
