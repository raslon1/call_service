from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import enum
import uuid
from app.database import Base
from datetime import datetime


class CallStatus(str, enum.Enum):
    CREATED = "created"
    PROCESSING = "processing"
    READY = "ready"


class Call(Base):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    caller = Column(String, nullable=False)
    receiver = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False)
    status = Column(Enum(CallStatus), default=CallStatus.CREATED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    call_id = Column(UUID(as_uuid=True), nullable=False)
    filename = Column(String, nullable=False)
    duration = Column(Integer, nullable=True)  # Duration in seconds
    transcription = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)