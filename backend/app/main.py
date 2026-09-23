import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.redis import redis_client
from app.db.session import engine

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.exports import router as exports_router
from app.api.extractions import router as extractions_router
from app.core.middleware import RequestContextMiddleware
from app.core.logging import configure_logging
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.models import Document, ExtractionVersion, User  # noqa: F401
from app.workers.extraction_worker import worker_loop


@asynccontextmanager
async def lifespan(_: FastAPI):
	async with engine.begin() as connection:
		await connection.run_sync(Base.metadata.create_all)
	worker_task = None
	if settings.environment.lower() != "production":
		worker_task = asyncio.create_task(worker_loop())
	try:
		yield
	finally:
		if worker_task is not None:
			worker_task.cancel()
			try:
				await worker_task
			except asyncio.CancelledError:
				pass
		await redis_client.close()
		await engine.dispose()


configure_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RequestContextMiddleware)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(exports_router)
app.include_router(extractions_router)
