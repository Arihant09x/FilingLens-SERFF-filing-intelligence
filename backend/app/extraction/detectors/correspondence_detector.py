import re
from typing import Any


CORRESPONDENCE_TYPES = {
	"objection": "objection_letter",
	"response": "response_letter",
	"industry response": "industry_response",
	"filing note": "filing_note",
	"disposition": "disposition",
}


def detect_correspondence(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
	results = []
	for page in pages:
		for line in page.get("text", "").splitlines():
			lowered = line.lower()
			match = next(((needle, kind) for needle, kind in CORRESPONDENCE_TYPES.items() if needle in lowered), None)
			if not match:
				continue
			results.append({
				"type": match[1], "status": "detected", "created_by": None,
				"created_on": None, "submitted_date": None, "responded_by": None,
				"response_date": None, "page": page["page"], "confidence": 0.75,
				"text": line.strip(), "source": {"page": page["page"]},
			})
	return results
