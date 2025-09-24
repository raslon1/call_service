from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.v1.calls import router as calls_router
from app.database import engine, Base
import os
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Call Service",
    description="Сервис управления звонками и записями разговоров",
    version="1.0.0"
)

app.include_router(calls_router, prefix="/api/v1")

if os.path.exists(settings.RECORDINGS_DIR):
    app.mount("/recordings", StaticFiles(directory=settings.RECORDINGS_DIR), name="recordings")


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)