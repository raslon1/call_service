from app.core.config import settings
from uuid import UUID
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, update
from app.models.call import Call, Recording


async def update_recording_results_async(call_id: UUID, duration: int, transcription: str):
    engine = create_async_engine(settings.DATABASE_URL)
    
    async_session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False
    )
    
    session = async_session_factory()
    
    try:
        result = await session.execute(
            select(Recording).where(Recording.call_id == call_id)
        )
        recording = result.scalars().first()
        
        if recording:
            await session.execute(
                update(Recording)
                .where(Recording.id == recording.id)
                .values(duration=duration, transcription=transcription)
            )
            
            await session.execute(
                update(Call)
                .where(Call.id == call_id)
                .values(status="ready")
            )
            
            await session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error in async update_recording_results: {str(e)}")
        return False
    finally:
        await session.close()
        await engine.dispose()


def update_recording_results(call_id: UUID, duration: int, transcription: str):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(update_recording_results_async(call_id, duration, transcription))
        loop.close()
        return result
    except Exception as e:
        print(f"Error updating recording results: {str(e)}")
        return False