from fastapi import Request
from fastapi.responses import JSONResponse


async def validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
	return JSONResponse(status_code=422, content={"error": {"code": "validation_error", "message": str(exc)}})
