import re
from typing import Any


FIELD_ALIASES = {
	"serff tracking number": "serff_tracking_number",
	"state tracking number": "state_tracking_number",
	"company tracking number": "company_tracking_number",
	"company": "company",
	"state": "state",
	"product name": "product_name",
	"toi": "toi",
	"sub toi": "sub_toi",
	"filing type": "filing_type",
	"date submitted": "date_submitted",
	"serff status": "serff_status",
	"state status": "state_status",
	"disposition date": "disposition_date",
	"effective date": "effective_date",
}


def extract_metadata(pages: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
	metadata: dict[str, dict[str, Any]] = {}
	for page in pages:
		for line in page.get("text", "").splitlines():
			match = re.match(r"^\s*([^:]{2,50}):\s*(.+?)\s*$", line)
			if not match:
				continue
			field = FIELD_ALIASES.get(" ".join(match.group(1).lower().split()))
			if field and field not in metadata:
				metadata[field] = {"value": match.group(2), "source": {"page": page["page"]}}
	return metadata
