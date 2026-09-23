def find_inconsistent_metadata(metadata: dict) -> list[dict]:
	flags = []
	for key, value in metadata.items():
		values = value if isinstance(value, list) else [value]
		normalized = {str(item.get("value", item)).strip().lower() if isinstance(item, dict) else str(item).strip().lower() for item in values}
		if len(normalized) > 1:
			flags.append({"type": "inconsistent_metadata", "severity": "medium", "message": f"Metadata field '{key}' has inconsistent values", "field": key})
	return flags
