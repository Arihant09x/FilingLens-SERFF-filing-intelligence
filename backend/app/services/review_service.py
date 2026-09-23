from typing import Any

from app.extraction.review.review_radar import build_review_flags


def review_extraction(data: dict[str, Any]) -> list[dict[str, Any]]:
	return build_review_flags(data)
