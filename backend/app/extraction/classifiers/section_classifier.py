from app.extraction.detectors.serff_detector import classify_serff_heading


def classify_section(text: str) -> str:
	return classify_serff_heading(text) or "general"
