from app.extraction.review.consistency_checker import find_inconsistent_metadata
from app.extraction.review.expected_sections import EXPECTED_SERFF_SECTIONS


def build_review_flags(data: dict) -> list[dict]:
	flags = []
	for section in data.get("sections", []):
		confidence = section.get("confidence", 0)
		if confidence < 0.65:
			flags.append({"type": "low_confidence_heading", "severity": "medium", "message": f"Heading classification confidence is {confidence:.0%}", "page": section.get("page_start"), "confidence": confidence})
		if section.get("page_end", section.get("page_start")) > section.get("page_start", 0):
			flags.append({"type": "section_spanning_pages", "severity": "low", "message": "Section content spans multiple source pages", "page": section.get("page_start"), "confidence": confidence})
	for table in data.get("tables", []):
		if not table.get("rows") or table.get("confidence", 0) < 0.65:
			flags.append({"type": "table_extraction_uncertainty", "severity": "medium", "message": "Table structure may require review", "page": table.get("page"), "confidence": table.get("confidence", 0)})
	seen_types = {section.get("section_type") for section in data.get("sections", [])}
	for section_type in sorted(EXPECTED_SERFF_SECTIONS - seen_types):
		flags.append({"type": "missing_expected_serff_section", "severity": "low", "message": f"Expected SERFF section was not detected: {section_type}", "page": None, "confidence": 0.0})
	flags.extend(find_inconsistent_metadata(data.get("metadata", {})))
	attachments = data.get("attachments", [])
	seen_names: set[str] = set()
	for attachment in attachments:
		key = " ".join(attachment.get("name", "").lower().split())
		if key in seen_names:
			flags.append({"type": "possible_duplicate_attachment", "severity": "low", "message": f"Possible duplicate attachment: {attachment.get('name')}", "page": attachment.get("page"), "confidence": attachment.get("confidence", 0)})
		seen_names.add(key)
	responses = {item.get("type") for item in data.get("correspondence", [])}
	for item in data.get("correspondence", []):
		if item.get("type") == "response_letter" and "objection_letter" not in responses:
			flags.append({"type": "unmatched_correspondence_response", "severity": "medium", "message": "Response letter detected without a matching objection letter", "page": item.get("page"), "confidence": item.get("confidence", 0)})
	return flags
