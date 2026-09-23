from pathlib import Path

from app.core.config import BACKEND_DIR, get_settings


class LocalStorage:
	def __init__(self, root: str | None = None):
		configured_root = Path(root or get_settings().local_storage_path)
		self.root = configured_root if configured_root.is_absolute() else BACKEND_DIR / configured_root
		self.root.mkdir(parents=True, exist_ok=True)

	async def save(self, key: str, content: bytes) -> str:
		path = self.root / key
		path.write_bytes(content)
		return key

	async def read(self, key: str) -> bytes:
		return (self.root / key).read_bytes()

	async def delete(self, key: str) -> None:
		path = self.root / key
		if path.exists():
			path.unlink()
