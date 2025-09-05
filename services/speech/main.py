from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.api.routes import router
from app.infrastructure.config import Settings

def create_app() -> FastAPI:
    settings = Settings()
    
    app = FastAPI(
        title="Speech Service",
        description="Servicio de procesamiento de voz",
        version="1.0.0"
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routes
    app.include_router(router)
    
    return app

app = create_app()

# STT Streaming WebSocket
@app.websocket("/stt/stream")
async def stt_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Recibir chunk de audio
            audio_chunk = await websocket.receive_bytes()
            
            # Simular transcripción en tiempo real
            text = "Simulated transcription"
            
            # Enviar resultado
            await websocket.send_json({
                "text": text,
                "confidence": 0.95,
                "is_final": True
            })
    except Exception as e:
        await websocket.close()

# TTS Streaming WebSocket
@app.websocket("/tts/stream")
async def tts_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Recibir texto
            data = await websocket.receive_json()
            text = data.get("text", "")
            
            # Simular síntesis de voz
            audio_chunk = b"Simulated audio chunk"
            
            # Enviar chunk de audio
            await websocket.send_bytes(audio_chunk)
    except Exception as e:
        await websocket.close()

# STT Endpoint (no streaming)
@app.post("/stt")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: Optional[str] = "es",
    task: Optional[str] = "transcribe"
):
    # Simular transcripción
    return {
        "text": "Simulated transcription",
        "confidence": 0.95,
        "language": language,
        "duration_seconds": 1.5
    }

# TTS Endpoint (no streaming)
@app.post("/tts")
async def text_to_speech(
    text: str,
    voice: Optional[str] = "default",
    language: Optional[str] = "es"
):
    # Simular síntesis de voz
    async def fake_audio_stream():
        # Simular chunks de audio
        for _ in range(5):
            yield b"Simulated audio chunk"
            await asyncio.sleep(0.1)
    
    return StreamingResponse(
        fake_audio_stream(),
        media_type="audio/wav"
    )

# Configuración del modelo
@app.get("/config")
async def get_config():
    return {
        "stt_model": "whisper-large-v3",
        "stt_device": "cuda",
        "tts_provider": "coqui",
        "supported_languages": ["es", "en"],
        "max_audio_duration": 300
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )