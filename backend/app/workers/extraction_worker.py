# backend/app/workers/extraction_worker.py
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logging import get_logger
from app.workers.extraction_worker_core import worker_loop

logger = get_logger(__name__)

_worker_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _worker_task
    logger.info("worker_service_starting")
    _worker_task = asyncio.create_task(worker_loop())
    try:
        yield
    finally:
        logger.info("worker_service_stopping")
        if _worker_task and not _worker_task.done():
            _worker_task.cancel()
            try:
                await _worker_task
            except asyncio.CancelledError:
                pass


app = FastAPI(
    title="FilingLens Extraction Worker",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": "extraction-worker", "status": "alive"}


@app.get("/health")
async def health() -> dict[str, str]:
    running = _worker_task is not None and not _worker_task.done()
    return {
        "service": "extraction-worker",
        "status": "alive" if running else "degraded",
        "worker_task": "running" if running else "stopped",
    }