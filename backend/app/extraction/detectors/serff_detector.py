SERFF_SECTION_TYPES = {
	"table of contents": "table_of_contents",
	"filing at a glance": "filing_at_a_glance",
	"general information": "general_information",
	"company and contact": "company_contact",
	"filing description": "filing_description",
	"filing contact information": "filing_contact",
	"filing company information": "filing_company_information",
	"filing fees": "filing_fees",
	"correspondence summary": "correspondence_summary",
	"dispositions": "disposition",
	"disposition": "disposition",
	"objection letters": "objection_letters",
	"response letters": "response_letters",
	"filing notes": "filing_notes",
	"amendments": "amendments",
	"schedule": "schedule",
	"supporting document": "supporting_documents",
	"form attachments": "form_attachments",
	"correspondence attachment": "correspondence_attachments",
}


def classify_serff_heading(text: str) -> str | None:
	normalized = " ".join(text.lower().split()).rstrip(":")
	for label, section_type in SERFF_SECTION_TYPES.items():
		if normalized == label or normalized.startswith(f"{label} "):
			return section_type
	return None
