from pathlib import Path
from typing import Protocol


class Storage(Protocol):
	async def save(self, key: str, content: bytes) -> str: ...
	async def read(self, key: str) -> bytes: ...
	async def delete(self, key: str) -> None: ...


def safe_key(document_id: str, filename: str) -> str:
	return f"{document_id}.pdf"


def get_storage() -> Storage:
	from app.core.config import get_settings

	if get_settings().storage_backend.lower() == "s3":
		from app.storage.s3 import S3Storage
		return S3Storage()
	from app.storage.local import LocalStorage
	return LocalStorage()
