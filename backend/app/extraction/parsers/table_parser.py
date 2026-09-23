from typing import Any


def normalize_table(table: dict[str, Any]) -> dict[str, Any]:
	rows = table.get("rows", [])
	if not rows:
		return {**table, "columns": [], "rows": [], "confidence": 0.3}
	columns = [str(cell or "").strip() for cell in rows[0]]
	body = [[str(cell or "").strip() for cell in row] for row in rows[1:]]
	return {**table, "columns": columns, "rows": body, "confidence": 0.8 if columns else 0.4}
