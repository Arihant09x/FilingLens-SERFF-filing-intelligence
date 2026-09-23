import logging
import os
import sys
from typing import Any

import structlog
from structlog.contextvars import bind_contextvars, clear_contextvars, merge_contextvars


SENSITIVE_KEYS = {
	"password",
	"hashed_password",
	"access_token",
	"refresh_token",
	"jwt",
	"authorization",
	"database_url",
	"pdf_contents",
	"pdf_content",
	"file_contents",
}


def _scrub_sensitive(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
	"""Remove secrets and document contents before any renderer sees the event."""
	for key in list(event_dict):
		normalized = key.lower().replace("-", "_")
		if normalized in SENSITIVE_KEYS or normalized.endswith("_token"):
			event_dict[key] = "[REDACTED]"
	return event_dict


def configure_logging(*, json_logs: bool | None = None, level: str | None = None) -> None:
	"""Configure structlog and standard-library loggers once for the process."""
	use_json = json_logs if json_logs is not None else os.getenv("LOG_JSON", "false").lower() in {"1", "true", "yes"}
	log_level = getattr(logging, (level or os.getenv("LOG_LEVEL", "INFO")).upper(), logging.INFO)
	timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)
	processors = [
		merge_contextvars,
		structlog.stdlib.add_log_level,
		structlog.stdlib.add_logger_name,
		_scrub_sensitive,
		timestamper,
		structlog.processors.StackInfoRenderer(),
		structlog.processors.format_exc_info,
	]
	renderer = structlog.processors.JSONRenderer() if use_json else structlog.dev.ConsoleRenderer()

	structlog.configure(
		processors=[*processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
		logger_factory=structlog.stdlib.LoggerFactory(),
		wrapper_class=structlog.stdlib.BoundLogger,
		cache_logger_on_first_use=False,
	)
	formatter = structlog.stdlib.ProcessorFormatter(
		processor=renderer,
		foreign_pre_chain=processors,
	)
	handler = logging.StreamHandler(sys.stdout)
	handler.setFormatter(formatter)
	root = logging.getLogger()
	root.handlers.clear()
	root.addHandler(handler)
	root.setLevel(log_level)
	for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
		logger = logging.getLogger(logger_name)
		logger.handlers.clear()
		logger.propagate = True
		logger.setLevel(log_level)


def get_logger(name: str):
	return structlog.get_logger(name)


def bind_request_id(request_id: str) -> None:
	bind_contextvars(request_id=request_id)


def clear_request_context() -> None:
	clear_contextvars()
