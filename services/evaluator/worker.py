# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/evaluator/worker.py
# Worker del Evaluator: consume jobs de Redis -> arma contexto -> llama LLMs -> persiste resultados -> marca estado.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
import os, json, asyncio
from typing import Dict, Any, Optional

# Redis asíncrono
from redis.asyncio import Redis

# --> Import absolutos para evitar líos de ruta
from services.evaluator.app.infrastructure.repository import FileMockRepository, EvaluatorRepository
from services.evaluator.app.infrastructure.repository_supabase import SupabaseRepository
from services.evaluator.app.domain.entities.interview import Interview
from services.evaluator.app.infrastructure.llm_provider import run_evaluations

# --------------- Config por ENV ---------------
STREAM_NAME = os.getenv("EVALUATOR_STREAM", "evaluation_jobs")   # --> Nombre del stream/cola
GROUP_NAME  = os.getenv("EVALUATOR_GROUP", "evaluator_group")    # --> Consumer group
CONSUMER_ID = os.getenv("EVALUATOR_CONSUMER", "evaluator_worker_1")
REDIS_URI   = os.getenv("REDIS_URI", "redis://redis:6379/0")     # --> Ya en .env.example
REPO_KIND   = os.getenv("EVALUATOR_REPO", "supabase")            # --> "supabase" | "mock"
REEVALUATE  = os.getenv("EVALUATOR_REEVALUATE", "false").lower() == "true"  # --> Idempotencia simple (hoy informativa)

# =============== Helpers ===============

# ---------------
# SELECCION DE REPO MOCK O SUPA
# ---------------
def _select_repo() -> EvaluatorRepository:
    """
    Selección de backend de datos por ENV:
      - "mock"     -> FileMockRepository
      - default    -> SupabaseRepository
    """
    if REPO_KIND == "mock":
        return FileMockRepository()
    return SupabaseRepository()

async def _ensure_group(r: Redis) -> None:
    """
    Crea el consumer group si no existe (mkstream=True crea el stream si hace falta).
    Ignora error si el grupo ya existe.
    """
    try:
        await r.xgroup_create(STREAM_NAME, GROUP_NAME, id="$", mkstream=True)
    except Exception:
        pass  # --> No nos importa si ya estaba creado

async def _ack(r: Redis, entry_id: str):
    """Ack del mensaje procesado al consumer group (no interrumpe si falla)."""
    try:
        await r.xack(STREAM_NAME, GROUP_NAME, entry_id)
    except Exception:
        pass


# =============== Núcleo del procesamiento ===============

async def process_job(repo: EvaluatorRepository, payload: Dict[str, Any]):
    """
    Flujo por job:
      1) valida que venga 'interview_id'
      2) marca 'running'
      3) carga contexto -> Interview.from_dict
      4) run_evaluations (3 modelos, async)
      5) save_evaluation_results (DB si hay columnas; sino local)
      6) marca 'done' o 'error'
    """
    interview_id = payload.get("interview_id")                 # --> Extraemos ID
    if not interview_id:
        print("[Evaluator] WARNING: payload sin 'interview_id'. Se ignora.")
        return

    # Idempotencia simple: si no queremos re-evaluar, dejamos que el repo/DB lo defina con su status.
    # Para no depender de schema, acá sólo respetamos REEVALUATE=false => seguimos igual (el repo anotará "running").
    try:
        await repo.mark_evaluation_status(interview_id, "running")
    except Exception as e:
        print(f"[Evaluator] WARNING: no pude marcar running: {e}")

    # --> Estado 'running' al iniciar (si falla no cortamos)
    try:
        await repo.mark_evaluation_status(interview_id, "running")
    except Exception as e:
        print(f"[Evaluator] WARNING: no pude marcar running: {e}")

    try:
        ctx = await repo.get_interview_context(interview_id) # --> Dict con 5 claves
        interview = Interview.from_dict(ctx) # --> Entidad Interview completa

        interview = await run_evaluations(interview) # --> Llama a OpenAI/Gemini/OpenRouter

        await repo.save_evaluation_results(interview_id, interview.to_dict()) # --> Persistencia DB/archivo
        await repo.mark_evaluation_status(interview_id, "done") # --> Estado final OK

        print(f"[Evaluator] DONE interview_id={interview_id}")
    except Exception as e:
        await repo.mark_evaluation_status(interview_id, "error", str(e)) # --> Estado final con error
        print(f"[Evaluator] ERROR interview_id={interview_id}: {e}")

async def main():
    """
    Loop principal del worker:
      - Conecta a Redis
      - Asegura consumer group
      - Hace XREADGROUP bloqueante y procesa de a 1 mensaje
    """
    repo = _select_repo() # --> Elige backend (supabase/mock)
    r = Redis.from_url(REDIS_URI) # --> Cliente Redis
    await _ensure_group(r) # --> Crea grupo si falta
    print(f"[Evaluator] Worker online | stream={STREAM_NAME} group={GROUP_NAME} consumer={CONSUMER_ID} repo={REPO_KIND}")

    while True:
        try:
            resp = await r.xreadgroup(
                GROUP_NAME, CONSUMER_ID, # --> Grupo + consumer
                streams={STREAM_NAME: ">"}, # --> '>' = mensajes nuevos
                count=1, block=10_000 # --> 1 por vez, 10s de espera
            )
            if not resp:
                continue # --> Timeout: sigue loop

            _, entries = resp[0] # --> Tomamos primera lista de entries
            for entry_id, fields in entries:
                try:
                    payload_raw = fields.get(b"payload") or fields.get("payload")  # --> Soporta bytes/str
                    payload = json.loads(payload_raw if isinstance(payload_raw, str)
                                           else payload_raw.decode("utf-8"))
                except Exception:
                    payload = {} # --> Si no parsea, payload vacío

                await process_job(repo, payload) # --> Procesa el job
                await _ack(r, entry_id) # --> Ack al grupo
        except Exception as loop_err:
            print(f"[Evaluator] Worker loop error: {loop_err}")
            await asyncio.sleep(1) # --> Backoff básico y seguimos

if __name__ == "__main__":
    asyncio.run(main())
