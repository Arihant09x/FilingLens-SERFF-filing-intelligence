from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class Credentials(BaseModel):
	email: EmailStr
	password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
	id: UUID
	email: EmailStr
	is_active: bool

	model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str = "bearer"
