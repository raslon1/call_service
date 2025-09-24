from celery import Celery
from app.core.config import settings
from pydub import AudioSegment
import os
from uuid import UUID
import logging
from app.utils.recording import update_recording_results

from vosk import Model, KaldiRecognizer
import wave
import json

logger = logging.getLogger(__name__)

celery_app = Celery("worker", broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

def transcribe_with_vosk(audio_file_path):
    try:
        audio = AudioSegment.from_file(audio_file_path)
        
        audio_sample = audio[:20000]  # 20 seconds in milliseconds
        
        wav_path = audio_file_path + "_temp.wav"
        audio_sample.export(wav_path, format="wav")
        
        model_path = "/app/vosk_models/vosk-model-small-ru-0.22"
        if not os.path.exists(model_path):
            logger.error(f"Vosk model not found at {model_path}")
            os.remove(wav_path)
            return "Vosk model not found"
            
        model = Model(model_path=model_path)
        
        wf = wave.open(wav_path, "rb")
        
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            logger.error("Audio file must be WAV format mono PCM.")
            wf.close()
            os.remove(wav_path)
            return "Audio format error"
        
        rec = KaldiRecognizer(model, wf.getframerate())
        
        results = []
        chunk_size = 4000
        data = wf.readframes(chunk_size)
        
        while len(data) > 0:
            data = wf.readframes(chunk_size)
            if rec.AcceptWaveform(data):
                result = rec.Result()
                results.append(json.loads(result))
        
        final_result = rec.FinalResult()
        results.append(json.loads(final_result))
        
        wf.close()
        
        os.remove(wav_path)
        
        transcript_parts = []
        for result in results:
            if 'text' in result and result['text'].strip():
                transcript_parts.append(result['text'])
        
        transcription = " ".join(transcript_parts)
        return transcription if transcription else "No speech detected"
        
    except Exception as e:
        logger.error(f"Error in Vosk transcription: {str(e)}")
        return "Transcription error"


@celery_app.task
def process_recording(call_id: str, filename: str):
    file_path = os.path.join(settings.RECORDINGS_DIR, filename)

    audio = AudioSegment.from_file(file_path)

    duration = len(audio) / 1000.0

    transcription = transcribe_with_vosk(file_path)

    success = update_recording_results(UUID(call_id), int(duration), transcription)

    return {
        "call_id": call_id,
        "duration": duration,
        "transcription": transcription,
        "status": "completed" if success else "failed"
    }