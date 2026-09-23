import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from app.core.config import settings
from app.core.logging import get_logger
from app.db.redis import redis_client

logger = get_logger(__name__)


class JobQueue:
    """Redis-backed extraction queue with a local fallback for test only."""

    def __init__(self, queue_name: str = "extraction_jobs") -> None:
        self.queue_name = queue_name
        self._jobs: dict[str, str] = {}
        self._local_queue: asyncio.Queue[str] = asyncio.Queue()

    async def enqueue(self, document_id: str, *, request_id: str | None = None) -> str:
        job_id = str(uuid4())
        payload = {
            "job_id": job_id,
            "document_id": str(document_id),
            "request_id": request_id,
            "queued_at": datetime.now(timezone.utc).isoformat(),
        }
        self._jobs[job_id] = "queued"
        try:
            await redis_client.rpush(self.queue_name, json.dumps(payload))
            logger.info(
                "job_enqueued",
                queue=self.queue_name,
                job_id=job_id,
                document_id=str(document_id),
                request_id=request_id,
            )
        except Exception:
            if settings.environment.lower() != "test":
                logger.exception(
                    "redis_enqueue_failed",
                    queue=self.queue_name,
                    job_id=job_id,
                    document_id=str(document_id),
                )
                raise
            logger.warning(
                "redis_unavailable_using_local_queue",
                queue=self.queue_name,
                job_id=job_id,
            )
            await self._local_queue.put(json.dumps(payload))
        return job_id

    async def dequeue(self, timeout: int = 5) -> dict[str, Any] | None:
        try:
            result = await redis_client.blpop(self.queue_name, timeout=timeout)
            if not result:
                # Expected: no job arrived within the blocking window. Quiet log.
                logger.debug("dequeue_empty", queue=self.queue_name, timeout=timeout)
                return None
            _, payload = result
            data = json.loads(payload)
            logger.info(
                "job_dequeued",
                queue=self.queue_name,
                job_id=data.get("job_id"),
                document_id=data.get("document_id"),
                request_id=data.get("request_id"),
            )
            return data
        except Exception:
            if settings.environment.lower() != "test":
                logger.exception(
                    "redis_dequeue_failed",
                    queue=self.queue_name,
                    timeout=timeout,
                )
                raise
            try:
                payload = await asyncio.wait_for(
                    self._local_queue.get(), timeout=timeout
                )
                logger.info("job_dequeued_local", queue=self.queue_name)
                return json.loads(payload)
            except asyncio.TimeoutError:
                return None

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