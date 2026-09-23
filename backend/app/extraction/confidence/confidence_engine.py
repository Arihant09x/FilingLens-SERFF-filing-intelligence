def score_heading(*, font_score: float, bold_score: float, position_score: float,
				  length_score: float, numbering_score: float, serff_score: float,
				  context_score: float) -> float:
	value = (
		font_score * 0.30 + bold_score * 0.20 + position_score * 0.15
		+ length_score * 0.10 + numbering_score * 0.10 + serff_score * 0.10
		+ context_score * 0.05
	)
	return round(max(0.0, min(1.0, value)), 2)


def confidence_label(value: float) -> str:
	if value >= 0.85:
		return "high"
	if value >= 0.65:
		return "medium"
	return "low"
