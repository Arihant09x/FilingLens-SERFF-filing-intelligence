from time import perf_counter
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import bind_request_id, clear_request_context, get_logger

logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		request_id = request.headers.get("x-request-id", str(uuid4()))
		bind_request_id(request_id)
		request.state.request_id = request_id
		started = perf_counter()
		logger.info("request_started", method=request.method, path=request.url.path)
		try:
			response = await call_next(request)
		except Exception:
			duration_ms = round((perf_counter() - started) * 1000, 2)
			logger.exception("request_finished", method=request.method, path=request.url.path, status_code=500, duration_ms=duration_ms)
			raise
		else:
			duration_ms = round((perf_counter() - started) * 1000, 2)
			logger.info("request_finished", method=request.method, path=request.url.path, status_code=response.status_code, duration_ms=duration_ms)
			response.headers["X-Request-ID"] = request_id
			response.headers["X-Content-Type-Options"] = "nosniff"
			response.headers["X-Frame-Options"] = "DENY"
			response.headers["Referrer-Policy"] = "same-origin"
			return response
		finally:
			clear_request_context()
