import re
from typing import Any

from app.extraction.classifiers.attachment_classifier import classify_attachment


def extract_attachments(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
	attachments = []
	for page in pages:
		for line in page.get("text", "").splitlines():
			if not re.search(r"\b(form|attachment|supporting document|correspondence)\b", line, re.IGNORECASE):
				continue
			if len(line.strip()) < 5:
				continue
			attachments.append({
				"name": line.strip(), "category": classify_attachment(line), "status": "detected",
				"public_access": None, "page": page["page"], "confidence": 0.72,
				"source": {"page": page["page"]},
			})
	return _deduplicate(attachments)


def _deduplicate(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
	seen: set[str] = set()
	unique = []
	for item in items:
		key = " ".join(item["name"].lower().split())
		if key not in seen:
			seen.add(key)
			unique.append(item)
	return unique
