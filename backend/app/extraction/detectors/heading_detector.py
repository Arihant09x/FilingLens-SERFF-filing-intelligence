import re
from typing import Any

from app.extraction.confidence.confidence_engine import score_heading
from app.extraction.detectors.serff_detector import classify_serff_heading


def detect_headings(page: dict[str, Any]) -> list[dict[str, Any]]:
	words = page.get("words", [])
	lines: dict[tuple[int, int], list[dict[str, Any]]] = {}
	for word in words:
		key = (round(float(word.get("top", 0)) // 3), round(float(word.get("bottom", 0)) // 3))
		lines.setdefault(key, []).append(word)

	sizes = [float(word.get("size", 0)) for word in words if word.get("size")]
	median_size = sorted(sizes)[len(sizes) // 2] if sizes else 10.0
	headings = []
	for line_words in lines.values():
		line_words.sort(key=lambda item: float(item.get("x0", 0)))
		text = " ".join(word.get("text", "") for word in line_words).strip()
		if not text or len(text) > 180:
			continue
		max_size = max(float(word.get("size", median_size)) for word in line_words)
		bold = any("bold" in word.get("fontname", "").lower() for word in line_words)
		serff_type = classify_serff_heading(text)
		numbered = bool(re.match(r"^(?:\d+(?:\.\d+)*|[A-Z][.)])\s", text))
		size_score = min(1.0, max_size / max(median_size * 1.35, 1))
		confidence = score_heading(
			font_score=size_score,
			bold_score=1.0 if bold else 0.25,
			position_score=1.0 if float(line_words[0].get("top", 0)) < page.get("height", 800) * 0.85 else 0.4,
			length_score=1.0 if 2 <= len(text) <= 90 else 0.5,
			numbering_score=1.0 if numbered else 0.2,
			serff_score=1.0 if serff_type else 0.0,
			context_score=0.8 if text[:1].isupper() else 0.2,
		)
		if serff_type or bold or max_size >= median_size * 1.2 or numbered:
			headings.append({
				"text": text,
				"section_type": serff_type or "general",
				"confidence": confidence,
				"source": {"page": page["page"], "bbox": [
					float(line_words[0].get("x0", 0)), float(line_words[0].get("top", 0)),
					float(line_words[-1].get("x1", 0)), float(line_words[-1].get("bottom", 0)),
				]},
			})
	return sorted(headings, key=lambda item: item["source"]["bbox"][1])
