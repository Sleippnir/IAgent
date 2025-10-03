# Endpoints de /api/v1/technical_questions_answers_jobs. Inyecta el repo Postgres real.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from ..models.techqa_job import TechQAJobLink, TechQAJobLinkResponse
from ...infrastructure.persistence.postgres.postgres_techqa_job_repository import (
    link, unlink, list_by_job, list_by_techqa
)

# El gateway construye /api/v1/core/techqa-jobs → Core /api/v1/techqa-jobs. :contentReference[oaicite:3]{index=3}
router = APIRouter(prefix="/api/v1/techqa-jobs", tags=["techQA-jobs"])  

# ==========================
# DI (Dependency Injection)
# ==========================
def get_repo():
    """
    Funcion que se encarga de devolver un dict con referencias a las funciones CRUD para simplificar.
    """
    return {
        "link": link,
        "unlink": unlink,
        "list_by_job": list_by_job,
        "list_by_techqa": list_by_techqa
    }

# ==============================
# Endpoint 1: LINKEAR Pregunta 
# ==============================
@router.post("/link", response_model=TechQAJobLinkResponse, status_code=status.HTTP_201_CREATED)
async def link_question(payload: TechQAJobLink, repo = Depends(get_repo)):
    """
    Crea (o asegura) el vínculo entre un Job y una Tech Question & Answer.

    - **Body (TechQAJobLink)**: `job_id`, `techqa_id`
    - **Comportamiento**: idempotente mediante *upsert*. Si el link ya existe, lo retorna igual.
    - **Response 201 (TechQAJobLinkResponse)**: objeto de relación (ids, timestamps, etc.)
    - **Errores**: 400 si el payload es inválido, 409 si hay conflicto no recuperable.

    Ejemplo (cURL):
      curl -X POST /link -H "Content-Type: application/json" \
        -d '{"job_id":"<uuid-job>","techqa_id":"<uuid-techqa>"}'
    """
    row = await repo["link"](payload.job_id, payload.techqa_id)
    return row

# ==============================
# Endpoint 2: Eliminar LINK 
# ==============================
@router.delete("/link", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_question(payload: TechQAJobLink, repo = Depends(get_repo)):
    """
    Elimina el vínculo entre un Job y una Tech Question & Answer.

    - **Body (TechQAJobLink)**: `job_id`, `techqa_id`
    - **Response 204**: link eliminado correctamente (sin contenido).
    - **Errores**:
        - 404 si el vínculo no existe.
        - 400 si el payload es inválido.

    Ejemplo (cURL):
      curl -X DELETE /link -H "Content-Type: application/json" \
        -d '{"job_id":"<uuid-job>","techqa_id":"<uuid-techqa>"}'
    """
    ok = await repo["unlink"](payload.job_id, payload.techqa_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Link not found")
    return

# ==============================
# Endpoint 3: OBTENER LINK de job 
# ==============================
@router.get("/by-job/{job_id}", response_model=List[TechQAJobLinkResponse])
async def list_links_by_job(job_id: str,
                            repo = Depends(get_repo),
                            limit: int = Query(200, ge=1, le=1000),
                            offset: int = Query(0, ge=0)):
    """
    Lista todos los vínculos (Job ↔ TechQA) asociados a un Job específico.

    - **Path**: `job_id` (UUID/ID del Job)
    - **Query**: `limit` (1..1000, default 200), `offset` (>=0)
    - **Response 200 (List[TechQAJobLinkResponse])**: arreglo de relaciones; puede ser vacío.
    - **Errores**: 400 si los parámetros son inválidos; 404 opcional si `job_id` no existe (según política).

    Ejemplo (cURL):
      curl "/by-job/<uuid-job>?limit=100&offset=0"
    """
    rows = await repo["list_by_job"](job_id, limit=limit, offset=offset)
    return rows

# ==============================
# Endpoint 4: OBTENER LINK de techqa 
# ==============================
@router.get("/by-techqa/{techqa_id}", response_model=List[TechQAJobLinkResponse])
async def list_links_by_techqa(techqa_id: str,
                               repo = Depends(get_repo),
                               limit: int = Query(200, ge=1, le=1000),
                               offset: int = Query(0, ge=0)):
    """
    Lista todos los vínculos (Job ↔ TechQA) asociados a una Tech Question & Answer específica.

    - **Path**: `techqa_id` (UUID/ID de la TechQA)
    - **Query**: `limit` (1..1000, default 200), `offset` (>=0)
    - **Response 200 (List[TechQAJobLinkResponse])**: arreglo de relaciones; puede ser vacío.
    - **Errores**: 400 si los parámetros son inválidos; 404 opcional si `techqa_id` no existe (según política).

    Ejemplo (cURL):
      curl "/by-techqa/<uuid-techqa>?limit=50&offset=0"
    """
    rows = await repo["list_by_techqa"](techqa_id, limit=limit, offset=offset)
    return rows
