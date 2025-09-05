from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.api.routes import router
from app.infrastructure.config import Settings

def create_app() -> FastAPI:
    settings = Settings()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Incluir rutas
    app.include_router(router)
    
    return app

app = create_app()