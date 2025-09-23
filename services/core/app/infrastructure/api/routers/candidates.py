# Router de API para "candidates".
# Solo se detalla el esqueletio, prefijo, DI del repositorio y health local
from fastapi import APIRouter, Depends # --> APIRouter define el grupo de rutas; Depends inyecta dependencias (el repo o los use cases).
# Importamos el repo real de Supabase/Postgres
from ...infrastructure.persistence.postgres.postgres_candidate_repository import (
    get, list, create, update, delete  # Funciones CRUD que ya implementamos
)
from typing import List
from ..models.candidate import CandidateResponse, CandidateCreate, CandidateResponse
from fastapi import Query
from fastapi import status, HTTPException
from uuid import uuid4
from datetime import datetime

# El gateway construye /api/v1/core/candidates → Core /api/v1/candidates. :contentReference[oaicite:0]{index=0}
router = APIRouter(prefix="/api/v1/candidates", tags=["candidates"])

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
async def candidates_health():
    return {"ok": True, "router": "candidates"}

# ==============================
# Endpoint 1: Listar Candidatos
# ==============================
@router.get("", response_model=List[CandidateResponse])
async def list_candidates(
    repo = Depends(get_repo),
    limit: int = Query(100, ge=1, le=500),   # paginación: tope 500 para evitar abusos
    offset: int = Query(0, ge=0),            # desplazamiento inicial
):
    """
    Función que se encarga de listar candidatos ordenados por timestamp_created DESC.
    """
    rows = await repo["list"](limit=limit, offset=offset)  # --> Aquí llamamos a la funcion LIST() del postgres_candidate_repository.py
 
    return rows

# ==============================================
# Endpoint 2: OBTENER 1 CANDIDATO POR ID (PK)
# ==============================================
@router.get("/{id}", response_model=CandidateResponse)
async def get_candidate(
    id: str, # path param: id del candidato (id_candidate en DB)
    repo = Depends(get_repo),
):
    """
    Función que se encarga de buscar un candidato por su PK.
    Si no existe devuelve 404.
    Utiliza el repo Postgres real (Supabase) que inyectamos anteriormente. 
    """
    row = await repo["get"](id)  # --> Aquí llamamos a la funcion GET() del postgres_candidate_repository.py
    if not row:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return row

# ============================
# Endpoint 3: CREAR CANDIDATO
# ============================
@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    payload: CandidateCreate,
    repo = Depends(get_repo),
):
    """
    Funcióno que se encarga de crear un candidato en Supabase/postgres usando el repo real.
    Generando el ID app-side (uuid4) para no depender de defaults de DB.
    """
    candidate_dict = {
        "id": str(uuid4()), # --> id_candidate en DB
        "name": payload.name,
        "last_name": payload.last_name,
        "email": payload.email,
        "phone_num": payload.phone_num,
        "linkedin_url": payload.linkedin_url,
        "resume": payload.resume, 
        "created_at": datetime.utcnow() # Timestamp_created en DB (si None, SQL usa now())
    }

    row = await repo["create"](candidate_dict)  # --> Aquí llamamos a la funcion CREATE() del postgres_candidate_repository.py
    return row

# ==============================================
# Endpoint 4: ACTUALIZAR (parcial estilo PATCH)
# ==============================================
@router.patch("/{id}", response_model=CandidateResponse, status_code=status.HTTP_200_OK)
async def update_candidate(
    id: str,
    payload: CandidateUpdate,
    repo = Depends(get_repo),
):
    """
    Función que se encarga de actualizar los campos del candidato indicado por PK.
    Si no existe, responde 404.
    """
    updated = await repo["update"](id, payload)  # --> Aquí llamamos a la funcion UPDATE() del postgres_candidate_repository.py
    if not updated:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return updated

# ==============================================
# Endpoint 5: BORRAR CANDIDATO POR ID
# ==============================================
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    id: str,
    repo = Depends(get_repo),
):
    """
    Función que se encarga de borrar un candidato por su PK.
    Devuelve 204, si borró OK. 404 si no existía. 
    """
    ok = await repo["delete"](id) # --> Aquí llamamos a la funcion DELETE() del postgres_candidate_repository.py
    if not ok:
        # Si no borró ninguna fila, no existía ese id.
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Candidate not found")
    # 204 No Content: sin body
    return