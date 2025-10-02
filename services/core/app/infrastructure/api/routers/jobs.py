# Endpoints de /api/v1/jobs. Inyecta el repo Postgres real.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from uuid import uuid4
from datetime import datetime
from ..models.job import JobCreate, JobUpdate, JobResponse # --> Modelos de API
from ...infrastructure.persistence.postgres.postgres_job_repository import (
    get, list, create, update, delete  # Repo real (funciones CRUD)
)

# El gateway construye /api/v1/core/jobs → Core /api/v1/jobs. :contentReference[oaicite:2]{index=2}
router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

# ==========================
# DI (Dependency Injection)
# ==========================
def get_repo():
    """
    Funcion que se encarga de devolver un dict con referencias a las funciones CRUD para simplificar.
    """
    return {
        "get": get,
        "list": list,
        "create": create,
        "update": update,
        "delete": delete,
    }

# Health específico de este router (útil para smoke-tests rápidos).
@router.get("/healthz")
async def jobs_health():
    return {"ok": True, "router": "jobs"}

# ==============================
# Endpoint 1: LISTAR JOBS
# ==============================
@router.get("", response_model=List[JobResponse])
async def list_jobs(
    repo = Depends(get_repo),
    limit: int = Query(100, ge=1, le=500),   # paginación: tope 500 para evitar abusos
    offset: int = Query(0, ge=0),            # desplazamiento inicial
):
    """
    Función que se encarga de listar jobs ordenados por timestamp_created DESC.
    """
    rows = await repo["list"](limit=limit, offset=offset) # --> Aquí llamamos a la funcion LIST() del postgres_job_repository.py
    return rows

# ==============================================
# Endpoint 2: OBTENER 1 JOB POR ID (PK)
# ==============================================
@router.get("/{id}", response_model=JobResponse)
async def get_job(
    id: str, # path param: id del job (id_job en DB)
    repo = Depends(get_repo)
):
    """
    Función que se encarga de buscar un job por su PK.
    Si no existe devuelve 404.
    Utiliza el repo Postgres real (Supabase) que inyectamos anteriormente. 
    """
    row = await repo["get"](id) # --> Aquí llamamos a la funcion GET() del postgres_job_repository.py
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
    return row

# ============================
# Endpoint 3: CREAR JOB
# ============================
@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreate,
    repo = Depends(get_repo)
):
    """
    Funcióno que se encarga de crear un job en Supabase/postgres usando el repo real.
    Generando el ID app-side (uuid4) para no depender de defaults de DB.
    """
    job_dict = {
        "id": str(uuid4()), # --> id_candidate en DB
        "job_role": payload.job_role,
        "description": payload.description,
        "created_at": datetime.utcnow() # Timestamp_created en DB (si None, SQL usa now())
    }
    row = await repo["create"](job_dict) # --> Aquí llamamos a la funcion CREATE() del postgres_job_repository.py
    return row

# ==============================================
# Endpoint 4: ACTUALIZAR (parcial estilo PATCH)
# ==============================================
@router.patch("/{id}", response_model=JobResponse, status_code=status.HTTP_200_OK)
async def update_job(
    id: str,
    payload: JobUpdate,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de actualizar los campos del job indicado por PK.
    Si no existe, responde 404
    """
    updated = await repo["update"](id, payload) # --> Aquí llamamos a la funcion UPDATE() del postgres_job_repository.py
    if not updated:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated

# ==============================================
# Endpoint 5: BORRAR JOB POR ID
# ==============================================
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    id: str,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de borrar un job por su PK.
    Devuelve 204, si borró OK. 404 si no existía. 
    """
    ok = await repo["delete"](id) # --> Aquí llamamos a la funcion DELETE() del postgres_job_repository.py
    if not ok:
        raise HTTPException(status_code=404, detail="Job not found")
    # 204 No Content: sin body
    return