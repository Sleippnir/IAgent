from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
import soundfile as sf
import io
from .models import AudioCreate, AudioResponse, TranscriptionSegment
from ...application.use_cases.audio_use_cases import AudioUseCases
from ..persistence.mongodb.audio_repository import MongoDBAudioRepository
from ..config import Settings

router = APIRouter(prefix="/api/v1")
settings = Settings()

def get_use_cases() -> AudioUseCases:
    repository = MongoDBAudioRepository()
    return AudioUseCases(repository)

@router.get("/healthz")
def health_check():
    return {"status": "ok", "service": "speech"}

@router.post("/audio", response_model=AudioResponse)
async def upload_audio(
    file: UploadFile = File(...),
    use_cases: AudioUseCases = Depends(get_use_cases)
):
    if file.size > settings.MAX_AUDIO_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    content = await file.read()
    format = file.filename.split('.')[-1].lower()
    
    if format not in settings.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    try:
        with io.BytesIO(content) as buffer:
            data, sample_rate = sf.read(buffer)
            duration = len(data) / sample_rate
            channels = 1 if len(data.shape) == 1 else data.shape[1]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid audio file: {str(e)}")
    
    return await use_cases.create_audio(
        content=content,
        sample_rate=sample_rate,
        channels=channels,
        format=format,
        duration=duration
    )

@router.get("/audio/{audio_id}", response_model=AudioResponse)
async def get_audio(audio_id: str, use_cases: AudioUseCases = Depends(get_use_cases)):
    audio = await use_cases.get_audio(audio_id)
    if not audio:
        raise HTTPException(status_code=404, detail="Audio not found")
    return audio

@router.get("/audio", response_model=List[AudioResponse])
async def list_audio(use_cases: AudioUseCases = Depends(get_use_cases)):
    return await use_cases.list_audio()