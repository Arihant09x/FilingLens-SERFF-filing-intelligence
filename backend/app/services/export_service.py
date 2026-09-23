import csv
import io
import json


def as_json(data: dict) -> str:
	return json.dumps(data, indent=2, default=str)


def as_csv(data: dict) -> str:
	output = io.StringIO()
	writer = csv.writer(output)
	writer.writerow(["record_type", "heading", "page", "text", "confidence"])
	for section in data.get("sections", []):
		writer.writerow(["section", section.get("heading"), section.get("page_start"), section.get("text", ""), section.get("confidence")])
	for table in data.get("tables", []):
		writer.writerow(["table", table.get("title"), table.get("page"), json.dumps(table.get("rows", [])), table.get("confidence")])
	return output.getvalue()


def as_markdown(data: dict) -> str:
	lines = ["# Filing", "", "## Metadata", ""]
	for key, value in data.get("metadata", {}).items():
		lines.append(f"- **{key}**: {value.get('value', '')}")
	lines.extend(["", "## Sections", ""])
	for section in data.get("sections", []):
		lines.extend([f"### {section['heading']}", f"_Page {section['page_start']}_", "", section.get("text", ""), ""])
	lines.extend(["## Tables", ""])
	for table in data.get("tables", []):
		lines.append(f"- {table.get('title', 'Table')} (page {table.get('page')})")
	lines.extend(["", "## Review Flags", ""])
	for flag in data.get("review_flags", []):
		lines.append(f"- **{flag['severity']}** {flag['message']}")
	return "\n".join(lines)
