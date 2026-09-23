from pathlib import Path
from typing import Any

from app.extraction.detectors.heading_detector import detect_headings
from app.extraction.detectors.metadata_detector import extract_metadata
from app.extraction.detectors.section_detector import build_sections
from app.extraction.detectors.correspondence_detector import detect_correspondence
from app.extraction.parsers.attachment_parser import extract_attachments
from app.extraction.parsers.table_parser import normalize_table
from app.extraction.review.review_radar import build_review_flags
from app.extraction.parsers.pdf_parser import parse_pdf


def run_extraction(path: str | Path) -> dict[str, Any]:
	parsed = parse_pdf(path)
	headings = []
	for page in parsed["pages"]:
		headings.extend([{**heading, "page": page["page"]} for heading in detect_headings(page)])
	sections = build_sections(headings, parsed["pages"])
	tables = [normalize_table({**table, "title": "Detected table"}) for page in parsed["pages"] for table in page["tables"]]
	data: dict[str, Any] = {
		"metadata": extract_metadata(parsed["pages"]),
		"sections": sections,
		"tables": tables,
		"attachments": extract_attachments(parsed["pages"]),
		"correspondence": detect_correspondence(parsed["pages"]),
		"pages": [{"page": page["page"], "text": page["text"]} for page in parsed["pages"]],
	}
	data["review_flags"] = build_review_flags(data)
	confidences = [section["confidence"] for section in sections]
	data["snapshot"] = {
		"section_count": len(sections), "table_count": len(tables),
		"attachment_count": len(data["attachments"]), "correspondence_count": len(data["correspondence"]),
		"average_confidence": round(sum(confidences) / len(confidences), 2) if confidences else 0,
		"low_confidence_count": sum(confidence < 0.65 for confidence in confidences),
		"review_flag_count": len(data["review_flags"]), "page_count": parsed["page_count"],
	}
	return data
