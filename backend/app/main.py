# app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.exports import router as exports_router
from app.api.extractions import router as extractions_router
from app.api.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware
from app.db.redis import redis_client
from app.db.session import engine

# NOTE: no worker import here. The API never runs the extraction loop.


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup: nothing to do. Schema is managed by Alembic, not create_all.
    yield
    # Shutdown: close Redis and dispose the DB engine cleanly.
    await redis_client.aclose()   # was: close() — aclose() is the asyncio-correct name
    await engine.dispose()


configure_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestContextMiddleware)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(exports_router)
app.include_router(extractions_router)