from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class CallCreate(BaseModel):
    caller: str = Field(..., example="+79001234567")
    receiver: str = Field(..., example="+74951234567")
    started_at: datetime = Field(..., example="2025-09-20T10:00:00")


class RecordingInfo(BaseModel):
    filename: str
    duration: Optional[int] = None
    transcription: Optional[str] = None
    presigned_url: Optional[str] = None


class CallResponse(BaseModel):
    id: UUID
    caller: str
    receiver: str
    started_at: datetime
    recording: Optional[RecordingInfo] = None

    class Config:
        from_attributes = True