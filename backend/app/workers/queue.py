from collections.abc import Awaitable, Callable
from typing import Any


class JobQueue:
	"""Small queue adapter; replace submit with Redis/Celery in production."""

	def __init__(self) -> None:
		self._jobs: dict[str, str] = {}

	def status(self, job_id: str) -> str:
		return self._jobs.get(job_id, "unknown")

	async def submit(self, job_id: str, task: Callable[[], Awaitable[Any]]) -> None:
		self._jobs[job_id] = "queued"
		self._jobs[job_id] = "processing"
		try:
			await task()
		except Exception:
			self._jobs[job_id] = "failed"
			raise
		self._jobs[job_id] = "completed"


queue = JobQueue()
