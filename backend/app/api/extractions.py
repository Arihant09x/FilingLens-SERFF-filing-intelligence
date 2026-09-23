from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.repositories.document import get_owned
from app.db.repositories.extraction import list_versions
from app.db.session import get_db
from app.models.user import User
from app.schemas.extraction import ExtractionRead

router = APIRouter(prefix="/api/v1/documents", tags=["extractions"])


@router.get("/{document_id}/versions", response_model=list[ExtractionRead])
async def versions(document_id: UUID, user: Annotated[User, Depends(get_current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
	if await get_owned(db, document_id, user.id) is None:
		raise HTTPException(status_code=404, detail="Document not found")
	return await list_versions(db, document_id)
