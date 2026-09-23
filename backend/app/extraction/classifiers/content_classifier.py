import re


def classify_content(text: str) -> str:
	if not text.strip():
		return "empty"
	if re.search(r"\b(table|schedule|amount|fee)\b", text, re.IGNORECASE):
		return "structured"
	return "body"
