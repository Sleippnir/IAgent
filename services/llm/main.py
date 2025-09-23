from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.api.routes import router
from app.infrastructure.config import Settings
import uvicorn

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

# Health check
@app.get("/healthz")
async def health_check():
    return {"status": "healthy", "service": "llm"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )