from fastapi import APIRouter, HTTPException, UploadFile, File, Path, Query
from app.schemas.call import CallCreate, CallResponse
from app.use_cases.call import CallService

from uuid import UUID
import os
from app.core.config import settings
from app.worker.tasks import process_recording
from typing import List

router = APIRouter(prefix="/calls", tags=["calls"])

os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)


@router.post("/", response_model=CallResponse)
async def create_call(call_data: CallCreate):
    try:
        service = CallService()
        result = await service.create_call(call_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{call_id}/recording/")
async def upload_recording(
    call_id: UUID = Path(..., description="The ID of the call"),
    file: UploadFile = File(..., description="Audio file (mp3 or wav)")
):
    try:
        if file.content_type not in ["audio/mpeg", "audio/wav", "audio/mp3"]:
            raise HTTPException(status_code=400, detail="Only MP3 and WAV files are allowed")
        
        file_extension = file.filename.split(".")[-1]
        filename = f"{call_id}.{file_extension}"
        file_path = os.path.join(settings.RECORDINGS_DIR, filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        service = CallService()
        await service.upload_recording(call_id, filename)
        
        process_recording.delay(str(call_id), filename)
        
        return {"message": "Recording uploaded successfully", "filename": filename}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{call_id}/", response_model=CallResponse)
async def get_call(
    call_id: UUID = Path(..., description="The ID of the call")
):
    try:
        service = CallService()
        result = await service.get_call(call_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CallResponse])
async def search_calls(
    number: str = Query(..., description="Phone number to search for")
):
    try:
        service = CallService()
        results = await service.search_calls(number)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))