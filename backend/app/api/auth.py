from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Credentials, TokenResponse, UserResponse
from app.services.auth_service import authenticate, register, tokens_for
from app.core.rate_limit import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(credentials: Credentials, db: Annotated[AsyncSession, Depends(get_db)]):
	try:
		return await register(db, credentials.email, credentials.password)
	except ValueError as error:
		raise HTTPException(status_code=409, detail=str(error))


@router.post("/login", response_model=TokenResponse)
async def login(credentials: Credentials, db: Annotated[AsyncSession, Depends(get_db)]):
	try:
		limiter.check(f"login:{credentials.email.lower()}", 10)
	except RuntimeError:
		raise HTTPException(status_code=429, detail="Too many login attempts")
	user = await authenticate(db, credentials.email, credentials.password)
	if user is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
	return tokens_for(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(refresh_token: str, db: Annotated[AsyncSession, Depends(get_db)]):
	try:
		user_id = decode_token(refresh_token, "refresh")
	except (jwt.InvalidTokenError, ValueError):
		raise HTTPException(status_code=401, detail="Invalid refresh token")
	user = await db.get(User, user_id)
	if user is None or not user.is_active:
		raise HTTPException(status_code=401, detail="Invalid refresh token")
	return tokens_for(user)


@router.get("/me", response_model=UserResponse)
async def me(user: Annotated[User, Depends(get_current_user)]):
	return user
