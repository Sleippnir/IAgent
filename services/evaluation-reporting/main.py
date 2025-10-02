from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el .env principal primero
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
# Luego cargar variables locales del servicio (si existen)
load_dotenv()

app = FastAPI(title="Evaluation & Reporting Service")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/healthz")
def health_check():
    return {"status": "ok", "service": "evaluation-reporting"}
class EvaluationResult(BaseModel):
    interview_id: str
    candidate_id: str
    position: str
    scores: Dict[str, float]
    feedback: str
    created_at: datetime

class ExportRequest(BaseModel):
    interview_id: str
    format: str = "pdf"
    language: str = "es"

# Health check
@app.get("/healthz")
async def health_check():
    return {"status": "healthy"}

# Métricas
@app.get("/metrics")
async def metrics():
    return {
        "evaluations_total": 0,
        "reports_generated": 0,
        "avg_processing_time_ms": 0.0
    }

# Resultados de entrevista
@app.get("/results/interview/{interview_id}")
async def get_interview_results(interview_id: str):
    # Simular resultado de entrevista
    return {
        "interview_id": interview_id,
        "candidate_id": "candidate-123",
        "position": "Software Engineer",
        "scores": {
            "technical_knowledge": 0.85,
            "communication": 0.90,
            "problem_solving": 0.88,
            "experience": 0.82
        },
        "feedback": "Candidato demuestra sólidos conocimientos técnicos...",
        "created_at": datetime.now()
    }

# Resultados por candidato
@app.get("/results/candidate/{candidate_id}")
async def get_candidate_results(candidate_id: str):
    # Simular historial del candidato
    return {
        "candidate_id": candidate_id,
        "interviews": [
            {
                "interview_id": "interview-123",
                "position": "Software Engineer",
                "date": datetime.now(),
                "overall_score": 0.86
            }
        ]
    }

# Estadísticas globales
@app.get("/stats/global")
async def get_global_stats():
    return {
        "total_interviews": 100,
        "avg_score": 0.75,
        "positions": {
            "Software Engineer": 45,
            "Data Scientist": 30,
            "DevOps Engineer": 25
        },
        "success_rate": 0.68
    }

# Estadísticas por posición
@app.get("/stats/position/{position_id}")
async def get_position_stats(position_id: str):
    return {
        "position": "Software Engineer",
        "total_interviews": 45,
        "avg_score": 0.78,
        "key_skills": [
            {"name": "Python", "avg_score": 0.82},
            {"name": "System Design", "avg_score": 0.75},
            {"name": "Problem Solving", "avg_score": 0.80}
        ]
    }

# Exportar reporte
@app.post("/export/{interview_id}")
async def export_report(
    interview_id: str,
    request: ExportRequest,
    background_tasks: BackgroundTasks
):
    if request.format == "pdf":
        # Simular generación de PDF
        return FileResponse(
            "report.pdf",
            media_type="application/pdf",
            filename=f"report_{interview_id}.pdf"
        )
    elif request.format == "json":
        # Retornar JSON directamente
        return get_interview_results(interview_id)
    else:
        raise HTTPException(status_code=400, detail="Formato no soportado")

# Consumer de Redis Streams
class StreamConsumer:
    async def process_answers(self):
        # Implementar procesamiento de respuestas
        pass

    async def process_evaluations(self):
        # Implementar procesamiento de evaluaciones
        pass

# Inicializar consumer en startup
@app.on_event("startup")
async def startup_event():
    # Iniciar consumers de Redis Streams
    pass

if __name__ == "__main__":
    # Obtener configuración desde variables de entorno
    host = os.getenv("EVALUATION_SERVICE_HOST", os.getenv("EVALUATION_HOST", "0.0.0.0"))
    port = int(os.getenv("EVALUATION_SERVICE_PORT", os.getenv("EVALUATION_PORT", "8005")))
    
    print(f"Iniciando Evaluation Service en {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )