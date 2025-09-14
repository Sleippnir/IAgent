from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .infrastructure.api import routes

app = FastAPI(title="Orchestrator Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)