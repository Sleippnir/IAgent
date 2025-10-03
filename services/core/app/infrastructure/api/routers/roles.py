# Endpoints de /api/v1/roles. Inyecta el repo Postgres real.
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from ..models.user import RoleResponse
from ...persistence.postgres.postgres_role_repository import (
    get as repo_get,
    list as repo_list,
)
# El gateway construye /api/v1/core/roles → Core /api/v1/roles.
router = APIRouter(prefix="/api/v1/roles", tags=["roles"])

# ==========================
# DI (Dependency Injection)
# ==========================
def get_repo():
    """
    Funcion que se encarga de devolver un dict con referencias a las funciones CRUD para simplificar.
    """
    return {
        "get": get,
        "list": list
    }

# ==============================
# Endpoint 1: LISTAR ROLES
# ==============================
@router.get("", response_model=List[RoleResponse])
async def list_roles(
    repo = Depends(get_repo),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Función que se encarga de listar roles ordenados por timestamp_created DESC.
    """
    rows = await repo["list"](limit=limit, offset=offset) # --> Aquí llamamos a la funcion LIST() del postgres_role_repository.py
    return rows



# ==============================================
# Endpoint 2: OBTENER 1 ROLE POR ID (PK)
# ==============================================
@router.get("/{id}", response_model=RoleResponse)
async def get_role(
    id: str,
    repo = Depends(get_repo)
):
    """
    Función que se encarga de buscar un role por su PK.
    Si no existe devuelve 404.
    Utiliza el repo Postgres real (Supabase) que inyectamos anteriormente. 
    """
    row = await repo["get"](id) # --> Aquí llamamos a la funcion GET() del postgres_role_repository.py
    if not row:
        raise HTTPException(status_code=404, detail="Role not found")
    return row
