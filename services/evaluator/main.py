from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.api.routes import router
from app.infrastructure.api.evaluation_routes import router as evaluation_router
from app.infrastructure.api.reporting_routes import router as reporting_router
from app.infrastructure.config import get_settings
import uvicorn

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="Service for evaluating technical interviews using multiple LLM providers",
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
    app.include_router(evaluation_router)
    app.include_router(reporting_router)
    
    return app

app = create_app()

# Health check
@app.get("/healthz")
async def health_check():
    settings = get_settings()
    return {
        "status": "healthy", 
        "service": "llm-evaluation-service",
        "description": "Combined LLM Interview Evaluation and Reporting Service",
        "project_name": settings.PROJECT_NAME,
        "features": ["llm-evaluation", "reporting", "statistics"]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True
    )