# app/api/health.py
import asyncio

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.db.redis import redis_client
from app.db.session import engine

router = APIRouter(prefix="/api/v1/health", tags=["health"])


async def _check_db() -> tuple[bool, str]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("select 1"))
        return True, "ok"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


async def _check_redis() -> tuple[bool, str]:
    try:
        pong = await redis_client.ping()
        return (True, "ok") if pong else (False, "ping returned falsy")
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {exc}"


@router.get("")
async def health() -> dict[str, str]:
    # Liveness: process is up. No external calls.
    return {"status": "ok"}


@router.get("/ready")
async def ready(response: Response) -> dict:
    # Readiness: verify every dependency in parallel.
    (db_ok, db_msg), (redis_ok, redis_msg) = await asyncio.gather(
        _check_db(), _check_redis()
    )
    all_ok = db_ok and redis_ok

    if not all_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if all_ok else "not_ready",
        "checks": {
            "database": {"ok": db_ok, "detail": db_msg},
            "redis": {"ok": redis_ok, "detail": redis_msg},
        },
    }