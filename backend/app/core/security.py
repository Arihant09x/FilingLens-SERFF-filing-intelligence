from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt

from app.core.config import get_settings


def hash_password(password: str) -> str:
	return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
	return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: UUID, token_type: str, expires: timedelta) -> str:
	now = datetime.now(timezone.utc)
	return jwt.encode({"sub": str(user_id), "type": token_type, "iat": now, "exp": now + expires}, get_settings().jwt_secret, algorithm="HS256")


def decode_token(token: str, expected_type: str = "access") -> UUID:
	payload = jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
	if payload.get("type") != expected_type or not payload.get("sub"):
		raise jwt.InvalidTokenError("invalid token type")
	return UUID(payload["sub"])
