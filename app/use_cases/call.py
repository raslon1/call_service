from app.core.uow import SQLAlchemyUnitOfWork
from app.schemas.call import CallCreate, CallResponse, RecordingInfo
from uuid import UUID
from typing import List
from app.utils.storage import generate_presigned_url


class CallService:
    async def create_call(self, call_data: CallCreate) -> CallResponse:
        async with SQLAlchemyUnitOfWork() as uow:
            call = await uow.call_repo.create_call(
                caller=call_data.caller,
                receiver=call_data.receiver,
                started_at=call_data.started_at
            )
            await uow.commit()
            return CallResponse(
                id=call.id,
                caller=call.caller,
                receiver=call.receiver,
                started_at=call.started_at,
                recording=None
            )

    async def get_call(self, call_id: UUID) -> CallResponse:
        async with SQLAlchemyUnitOfWork() as uow:
            call = await uow.call_repo.get_call_by_id(call_id)
            if not call:
                raise ValueError("Call not found")
            
            recording_info = None
            recording = await uow.recording_repo.get_recording_by_call_id(call_id)
            if recording:
                presigned_url = generate_presigned_url(recording.filename)
                recording_info = RecordingInfo(
                    filename=recording.filename,
                    duration=recording.duration,
                    transcription=recording.transcription,
                    presigned_url=presigned_url
                )
            
            return CallResponse(
                id=call.id,
                caller=call.caller,
                receiver=call.receiver,
                started_at=call.started_at,
                recording=recording_info
            )

    async def upload_recording(self, call_id: UUID, filename: str) -> bool:
        async with SQLAlchemyUnitOfWork() as uow:
            call = await uow.call_repo.get_call_by_id(call_id)
            if not call:
                raise ValueError("Call not found")
            
            await uow.call_repo.update_call_status(call_id, "processing")
            
            recording = await uow.recording_repo.create_recording(call_id, filename)
            
            await uow.commit()
            return True

    async def search_calls(self, number: str) -> List[CallResponse]:
        async with SQLAlchemyUnitOfWork() as uow:
            calls = await uow.call_repo.search_calls_by_number(number)
            
            results = []
            for call in calls:
                recording_info = None
                recording = await uow.recording_repo.get_recording_by_call_id(call.id)
                if recording:
                    presigned_url = generate_presigned_url(recording.filename)
                    recording_info = RecordingInfo(
                        filename=recording.filename,
                        duration=recording.duration,
                        transcription=recording.transcription,
                        presigned_url=presigned_url
                    )
                
                results.append(CallResponse(
                    id=call.id,
                    caller=call.caller,
                    receiver=call.receiver,
                    started_at=call.started_at,
                    recording=recording_info
                ))
            
            return results