def classify_attachment(text: str) -> str:
	lowered = text.lower()
	if "correspondence" in lowered:
		return "correspondence"
	if "form" in lowered:
		return "form"
	return "supporting_document"
