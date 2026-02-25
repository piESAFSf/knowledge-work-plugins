import uuid

from sqlalchemy import JSON, ForeignKey, String, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class SecurityEvent(BaseModel):
    __tablename__ = 'security_events'

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='RESTRICT'),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    event_metadata: Mapped[dict | None] = mapped_column('metadata', JSON, nullable=True)


@event.listens_for(SecurityEvent, 'before_update', propagate=True)
def _prevent_security_event_update(*_):
    raise ValueError('SecurityEvent records are append-only')


@event.listens_for(SecurityEvent, 'before_delete', propagate=True)
def _prevent_security_event_delete(*_):
    raise ValueError('SecurityEvent records are append-only')
