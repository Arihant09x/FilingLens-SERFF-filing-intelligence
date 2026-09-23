from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_event import AuditEvent


async def record(db: AsyncSession, user_id: UUID, event_type: str, document_id: UUID | None = None, metadata: dict[str, Any] | None = None, ip_address: str | None = None) -> AuditEvent:
	event = AuditEvent(user_id=user_id, document_id=document_id, event_type=event_type, event_metadata=metadata or {}, ip_address=ip_address)
	db.add(event)
	await db.commit()
	await db.refresh(event)
	return event
