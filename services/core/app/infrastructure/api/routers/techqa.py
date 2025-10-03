# Endpoints de /api/v1/technical_questions_answers. Inyecta el repo Postgres real.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from ..models.techqa import TechQACreate, TechQAUpdate, TechQAResponse
from ...infrastructure.persistence.postgres.postgres_techqa_repository import (
    get, list, create, update, delete
)
# El gateway construye /api/v1/core/techqa → Core /api/v1/techqa. :contentReference[oaicite:2]{index=2}
router = APIRouter(prefix="/api/v1/techqa", tags=["techQA"])  

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
        "delete": delete
    }

# Health específico de este router (útil para smoke-tests rápidos).
@router.get("/healthz")
async def techqa_health():
    return {"ok": True, "router": "techqa"}

# ==============================
# Endpoint 1: LISTAR technical_questions_answers
# ==============================
@router.get("", response_model=List[TechQAResponse])
async def list_techqa(repo = Depends(get_repo),
                      limit: int = Query(100, ge=1, le=500),
                      offset: int = Query(0, ge=0),
                      q: Optional[str] = Query(None, description="buscar en pregunta/respuesta")):
    """
    Función que se encarga de listar technical_questions_answers ordenados por timestamp_created DESC.
    """
    rows = await repo["list"](limit=limit, offset=offset, q=q) # --> Aquí llamamos a la funcion LIST() del postgres_techqa_repository.py
    return rows 

# ==============================================
# Endpoint 2: OBTENER 1 technical_questions_answers POR ID (PK)
# ==============================================
@router.get("/{id}", response_model=TechQAResponse)
async def get_techqa(
    id: str,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de buscar un technical_questions_answers por su PK.
    Si no existe devuelve 404.
    Utiliza el repo Postgres real (Supabase) que inyectamos anteriormente. 
    """
    row = await repo["get"](id) # --> Aquí llamamos a la funcion GET() del postgres_techqa_repository.py
    if not row:
        raise HTTPException(status_code=404, detail="TechQA not found")
    return row

# ============================
# Endpoint 3: CREAR technical_questions_answers
# ============================
@router.post("", response_model=TechQAResponse, status_code=status.HTTP_201_CREATED)
async def create_techqa(
    payload: TechQACreate,
    repo = Depends(get_repo)
):
    """
    Funcióno que se encarga de crear un technical_questions_answers en Supabase/postgres usando el repo real.
    Generando el ID app-side (uuid4) para no depender de defaults de DB.
    """
    data = {
        "id": str(uuid4()),
        "question": payload.question,
        "answer": payload.answer,
        "created_at": datetime.utcnow()
    }
    row = await repo["create"](data) # --> Aquí llamamos a la funcion CREATE() del postgres_techqa_repository.py
    return row

# ==============================================
# Endpoint 4: ACTUALIZAR (parcial estilo PATCH)
# ==============================================
@router.patch("/{id}", response_model=TechQAResponse)
async def update_techqa(
    id: str,
    payload: TechQAUpdate,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de actualizar los campos del technical_questions_answers indicado por PK.
    Si no existe, responde 404
    """
    updated = await repo["update"](id, payload)
    if not updated:
        raise HTTPException(status_code=404, detail="TechQA not found") # --> Aquí llamamos a la funcion UPDATE() del postgres_techqa_repository.py
    return updated

# ==============================================
# Endpoint 5: BORRAR technical_questions_answers POR ID
# ==============================================
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_techqa(
    id: str,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de borrar un technical_questions_answers por su PK.
    Devuelve 204, si borró OK. 404 si no existía. 
    """
    ok = await repo["delete"](id) # --> Aquí llamamos a la funcion DELETE() del postgres_techqa_repository.py
    if not ok:
        raise HTTPException(status_code=404, detail="TechQA not found")
    # 204 No Content: sin body
    return
