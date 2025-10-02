# Endpoints de /api/v1/users. Inyecta el repo Postgres real.
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from uuid import uuid4
from datetime import datetime
import hashlib

from ..models.user import UserCreate, UserUpdate, UserResponse
from ...infrastructure.persistence.postgres.postgres_user_repository import (
    get, list, create, update, delete
)

# El gateway construye /api/v1/core/users → Core /api/v1/users.
router = APIRouter(prefix="/api/v1/users", tags=["users"])

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
async def users_health():
    return {"ok": True, "router": "users"}

# ==============================
# Endpoint 1: LISTAR USERS
# ==============================
@router.get("", response_model=List[UserResponse])
async def list_users(
    repo = Depends(get_repo),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Función que se encarga de listar users ordenados por timestamp_created DESC.
    """
    rows = await repo["list"](limit=limit, offset=offset)
    return rows

# ==============================================
# Endpoint 2: OBTENER 1 USERS POR ID (PK)
# ==============================================
@router.get("/{id}", response_model=UserResponse)
async def get_user(
    id: str,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de buscar un users por su PK.
    Si no existe devuelve 404.
    Utiliza el repo Postgres real (Supabase) que inyectamos anteriormente. 
    """
    row = await repo["get"](id) # --> Aquí llamamos a la funcion GET() del postgres_user_repository.py
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row

# ============================
# Endpoint 3: CREAR USERS
# ============================
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, repo = Depends(get_repo)):
    # Hash simple de password para DEMO. En producción, usar bcrypt/argon2.
    pwd_plain = payload.password.get_secret_value()
    pwd_hash = hashlib.sha256(pwd_plain.encode("utf-8")).hexdigest()
    """
    Funcióno que se encarga de crear un user en Supabase/postgres usando el repo real.
    Generando el ID app-side (uuid4) para no depender de defaults de DB.
    """
    user_dict = {
        "id": str(uuid4()),            # → id_user en DB; si DB lo genera, podés enviar None y ajustar repo
        "role_id": payload.role_id,    # → id_rol
        "name": payload.name,          # → name_user
        "email": payload.email,        # → email_user
        "password": pwd_hash,          # → password (hash)
        "created_at": datetime.utcnow()
    }
    row = await repo["create"](user_dict)
    return row


# ==============================================
# Endpoint 4: ACTUALIZAR (parcial estilo PATCH)
# ==============================================
@router.patch("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_user(
    id: str,
    payload: UserUpdate,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de actualizar los campos del user indicado por PK.
    Si no existe, responde 404
    """
    # REVISAR --> Si viene password, lo hasheamos igual que en create
    upd = payload.model_dump() 
    if upd.get("password") is not None:
        pwd_plain = payload.password.get_secret_value()
        upd["password"] = hashlib.sha256(pwd_plain.encode("utf-8")).hexdigest()

    updated = await repo["update"](id, upd) # --> Aquí llamamos a la funcion UPDATE() del postgres_user_repository.py
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return updated

# ==============================================
# Endpoint 5: BORRAR JOB POR ID
# ==============================================
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    id: str,
    repo = Depends(get_repo)
):  
    """
    Función que se encarga de borrar un user por su PK.
    Devuelve 204, si borró OK. 404 si no existía. 
    """
    ok = await repo["delete"](id) # --> Aquí llamamos a la funcion DELETE() del postgres_user_repository.py
    if not ok:
        raise HTTPException(status_code=404, detail="User not found")
    return
