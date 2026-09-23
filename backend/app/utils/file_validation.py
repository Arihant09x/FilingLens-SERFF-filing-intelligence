from app.core.config import get_settings


def validate_pdf(filename: str, content: bytes) -> None:
	if not filename.lower().endswith(".pdf"):
		raise ValueError("Only PDF files are supported")
	if not content or not content.startswith(b"%PDF-"):
		raise ValueError("The uploaded file is not a valid PDF")
	if len(content) > get_settings().max_upload_size_mb * 1024 * 1024:
		raise ValueError(f"File exceeds the {get_settings().max_upload_size_mb} MB limit")
