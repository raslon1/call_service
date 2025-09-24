from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.models.call import Call, Recording
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class CallRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_call(self, caller: str, receiver: str, started_at: datetime) -> Call:
        call = Call(caller=caller, receiver=receiver, started_at=started_at)
        self.db.add(call)
        await self.db.commit()
        await self.db.refresh(call)
        return call

    async def get_call_by_id(self, call_id: UUID) -> Optional[Call]:
        result = await self.db.execute(select(Call).where(Call.id == call_id))
        return result.scalars().first()

    async def update_call_status(self, call_id: UUID, status: str) -> Optional[Call]:
        await self.db.execute(
            update(Call).where(Call.id == call_id).values(status=status)
        )
        await self.db.commit()
        
        result = await self.db.execute(select(Call).where(Call.id == call_id))
        return result.scalars().first()

    async def search_calls_by_number(self, number: str) -> List[Call]:
        result = await self.db.execute(
            select(Call).where(
                (Call.caller == number) | (Call.receiver == number)
            )
        )
        return list(result.scalars().all())


class RecordingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_recording(self, call_id: UUID, filename: str) -> Recording:
        recording = Recording(call_id=call_id, filename=filename)
        self.db.add(recording)
        await self.db.commit()
        await self.db.refresh(recording)
        return recording

    async def get_recording_by_call_id(self, call_id: UUID) -> Optional[Recording]:
        result = await self.db.execute(select(Recording).where(Recording.call_id == call_id))
        return result.scalars().first()

    async def update_recording_processing_result(
        self, recording_id: UUID, duration: int, transcription: str
    ) -> Optional[Recording]:
        await self.db.execute(
            update(Recording)
            .where(Recording.id == recording_id)
            .values(duration=duration, transcription=transcription)
        )
        await self.db.commit()
        
        result = await self.db.execute(select(Recording).where(Recording.id == recording_id))
        return result.scalars().first()

    async def update_recording_processing_result_by_recording(
        self, recording: Recording, duration: int, transcription: str
    ) -> Optional[Recording]:
        await self.db.execute(
            update(Recording)
            .where(Recording.id == recording.id)
            .values(duration=duration, transcription=transcription)
        )
        await self.db.commit()
        
        result = await self.db.execute(select(Recording).where(Recording.id == recording.id))
        return result.scalars().first()