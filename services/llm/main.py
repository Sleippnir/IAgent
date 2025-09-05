from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.api.routes import router
from app.infrastructure.config import Settings

def create_app() -> FastAPI:
    settings = Settings()
    
    app = FastAPI(
        title="LLM Service",
        description="Servicio de procesamiento de lenguaje natural",
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

class Message(BaseModel):
    role: str
    content: str

class PromptRequest(BaseModel):
    role: str
    context: PromptContext
    history: List[Message]
    current_question: str

# Health check
@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

# Métricas
@app.get("/metrics")
async def metrics():
    return {
        "requests_total": 0,
        "tokens_total": 0,
        "avg_latency_ms": 0.0,
        "error_rate": 0.0
    }

# Generación síncrona
@app.post("/generate")
async def generate(request: PromptRequest):
    # Simular respuesta del LLM
    response = {
        "text": "Simulated LLM response",
        "tokens_used": 50,
        "provider": "openai",
        "model": "gpt-4"
    }
    return response

# Generación con streaming (SSE)
@app.post("/generate/stream")
async def generate_stream(request: PromptRequest):
    async def fake_llm_stream():
        # Simular streaming de tokens
        responses = [
            "Analizando ",
            "la pregunta ",
            "sobre ",
            request.context.position,
            "...\n",
            "Basado en ",
            "la experiencia ",
            "del candidato ",
            "en ",
            ", ".join(request.context.skills),
            "...\n",
            "Respuesta simulada."
        ]
        
        for chunk in responses:
            # Formato SSE
            data = json.dumps({"text": chunk, "is_final": False})
            yield f"data: {data}\n\n"
            await asyncio.sleep(0.1)
        
        # Mensaje final
        data = json.dumps({"text": "", "is_final": True})
        yield f"data: {data}\n\n"
    
    return StreamingResponse(
        fake_llm_stream(),
        media_type="text/event-stream"
    )

# Configuración de proveedores
@app.get("/providers")
async def list_providers():
    return {
        "providers": [
            {
                "name": "openai",
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "streaming": True
            },
            {
                "name": "anthropic",
                "models": ["claude-2", "claude-instant"],
                "streaming": True
            },
            {
                "name": "vllm",
                "models": ["llama2-70b"],
                "streaming": True
            }
        ],
        "default_provider": "openai",
        "default_model": "gpt-4"
    }

# Validación de prompts
@app.post("/validate")
async def validate_prompt(request: PromptRequest):
    return {
        "is_valid": True,
        "estimated_tokens": 100,
        "warnings": []
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True
    )