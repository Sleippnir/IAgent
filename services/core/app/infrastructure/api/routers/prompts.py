# Endpoints de /api/v1/prompts. Inyecta el repo Postgres real.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from uuid import uuid4
from datetime import datetime

from ..models.prompt import PromptCreate, PromptUpdate, PromptResponse # --> Modelos de API
from ...infrastructure.persistence.postgres.postgres_prompt_repository import (
    get, list, create, update, delete # Repo real (funciones CRUD)
)

# El gateway construye /api/v1/core/prompts → Core /api/v1/prompts.:contentReference[oaicite:1]{index=1}
router = APIRouter(prefix="/api/v1/prompts", tags=["prompts"])

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
async def prompts_health():
    return {"ok": True, "router": "prompts"}

# ==============================
# Endpoint 1: LISTAR PROMPTS
# ==============================
@router.get("", response_model=List[PromptResponse])
async def list_prompts(repo = Depends(get_repo),
                       limit: int = Query(100, ge=1, le=500),
                       offset: int = Query(0, ge=0)):
    """
    Función que se encarga de listar prompts ordenados por timestamp_created DESC.
    """
    rows = await repo["list"](limit=limit, offset=offset) # --> Aquí llamamos a la funcion LIST() del postgres_prompt_repository.py
    return rows

# ==============================================
# Endpoint 2: OBTENER 1 PROMPTS POR ID (PK)
# ==============================================
@router.get("/{id}", response_model=PromptResponse)
async def get_prompt(id: str, repo = Depends(get_repo)):
    """
    Función que se encarga de buscar un prompt por su PK.
    Si no existe devuelve 404.
    Utiliza el repo Postgres real (Supabase) que inyectamos anteriormente. 
    """
    row = await repo["get"](id) # --> Aquí llamamos a la funcion GET() del postgres_prompts_repository.py
    if not row:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return row

# ============================
# Endpoint 3: CREAR PROMPT
# ============================
@router.post("", response_model=PromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    payload: PromptCreate,
    repo = Depends(get_repo)
):
    """
    Funcióno que se encarga de crear un prompt en Supabase/postgres usando el repo real.
    Generando el ID app-side (uuid4) para no depender de defaults de DB.
    """
    p = {
        "id": str(uuid4()),
        "desc_prompt": payload.desc_prompt,
        "created_at": datetime.utcnow()
    }
    row = await repo["create"](p) # --> Aquí llamamos a la funcion CREATE() del postgres_prompt_repository.py
    return row


# ==============================================
# Endpoint 4: ACTUALIZAR (parcial estilo PATCH)
# ==============================================
@router.patch("/{id}", response_model=PromptResponse)
async def update_prompt(
    id: str,
    payload: PromptUpdate,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de actualizar los campos del prompt indicado por PK.
    Si no existe, responde 404
    """
    updated = await repo["update"](id, payload) # --> Aquí llamamos a la funcion UPDATE() del postgres_prompt_repository.py
    if not updated:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return updated


# ==============================================
# Endpoint 5: BORRAR PROMPT POR ID
# ==============================================
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    id: str,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de borrar un prompt por su PK.
    Devuelve 204, si borró OK. 404 si no existía. 
    """
    ok = await repo["delete"](id) # --> Aquí llamamos a la funcion DELETE() del postgres_prompt_repository.py
    if not ok:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return
