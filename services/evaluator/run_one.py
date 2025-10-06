# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/evaluator/run_one.py
# Ejecuta una evaluación directa por interview_id (sin Redis): ideal para demo/debug.
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*

import argparse, asyncio, os

# NICO --> Repositorios disponibles
from services.evaluator.app.infrastructure.repository import FileMockRepository
from services.evaluator.app.infrastructure.repository_supabase import SupabaseRepository

# NICO --> Orquestador de LLMs
from services.evaluator.app.infrastructure.llm_provider import run_evaluations

# NICO --> Entidad de dominio
from services.evaluator.app.domain.entities.interview import Interview


async def run_once(interview_id: str, repo_kind: str):
    # NICO --> Selección explícita del backend de datos
    #         "supabase" = SupabaseRepository (real), cualquier otro valor = mock
    use_supabase = (repo_kind or "").lower() == "supabase"
    repo = SupabaseRepository() if use_supabase else FileMockRepository()

    # NICO --> Estado inicial: running (DB o fallback local)
    await repo.mark_evaluation_status(interview_id, "running")

    # NICO --> Armar contexto (5 claves): interview_id, system_prompt, rubric, jd, full_transcript
    ctx = await repo.get_interview_context(interview_id)

    # NICO --> Entidad + evaluaciones
    interview = Interview.from_dict(ctx)
    interview = await run_evaluations(interview)

    # NICO --> Persistencia de resultados (DB preferente, fallback local si falta columna)
    await repo.save_evaluation_results(interview_id, interview.to_dict())

    # NICO --> Estado final
    await repo.mark_evaluation_status(interview_id, "done")
    print(f"[RunOne] DONE {interview_id}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True, help="ID de interview (INT en DB o demo-xxx en mock)")
    p.add_argument("--repo", default=os.getenv("EVALUATOR_REPO", "supabase"), help="supabase | mock")
    args = p.parse_args()

    # NICO --> Ejecuta el flujo asíncrono
    asyncio.run(run_once(args.id, args.repo))
