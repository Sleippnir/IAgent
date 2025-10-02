from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.infrastructure.api.routes import router
from app.infrastructure.config import Settings
import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el .env principal primero
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
# Luego cargar variables locales del servicio (si existen)
load_dotenv()

def create_app() -> FastAPI:
    settings = Settings()
    
    app = FastAPI(
        title="Core Service",
        description="Servicio central para gestión de entrevistas",
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

# Auth endpoints
@app.post("/auth/login")
async def login(email: str, password: str):
    # Implementar autenticación
    return {"access_token": "dummy_token", "token_type": "bearer"}

@app.post("/auth/refresh")
async def refresh_token(token: str = Depends(oauth2_scheme)):
    return {"access_token": "new_dummy_token", "token_type": "bearer"}

# User endpoints
@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"email": "user@example.com", "role": "admin"}

# Interview endpoints
@app.get("/interviews")
async def list_interviews(token: str = Depends(oauth2_scheme)):
    return [
        {
            "id": "interview-123",
            "candidate_email": "candidate@example.com",
            "position": "Software Engineer",
            "status": "scheduled",
            "created_at": datetime.now()
        }
    ]

@app.post("/interviews")
async def create_interview(interview: Interview, token: str = Depends(oauth2_scheme)):
    return interview

# Invite endpoints
@app.post("/invites/create")
async def create_invite(invite: Invite, token: str = Depends(oauth2_scheme)):
    return {
        "token": "dummy_invite_token",
        "expires_at": invite.expires_at
    }

@app.post("/invites/exchange")
async def exchange_invite(token: str):
    return {
        "interview_id": "interview-123",
        "access_token": "dummy_session_token"
    }

if __name__ == "__main__":
    # Obtener configuración desde variables de entorno
    host = os.getenv("CORE_SERVICE_HOST", os.getenv("CORE_HOST", "0.0.0.0"))
    port = int(os.getenv("CORE_SERVICE_PORT", os.getenv("CORE_PORT", "8001")))
    
    print(f"Iniciando Core Service en {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )