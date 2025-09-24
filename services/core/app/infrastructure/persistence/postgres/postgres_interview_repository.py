# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# services/core/app/infrastructure/persistence/postgres/postgres_interview_repository.py
# Repository real en Postgres (Supabase) para "interviews".
# Reemplaza al MongoDBInterviewRepository manteniendo la MISMA interfaz.
# Usa el pool creado en app.infrastructure.db (asyncpg).
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*
# --*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*--*


from __future__ import annotations
from typing import List, Optional, Any, Dict
from datetime import datetime

import asyncpg  # Driver async para Postgres
from app.infrastructure.db import Database  # Nuestro pool (lifespan lo inicializa)
from ....domain.entities.interview import Interview  # Entidad de dominio
from ....domain.repositories.interview_repository import InterviewRepository  # Interfaz/ABC

TABLE = "interviews" # --> Nombre de la tabla en Supabase

# Utilidad: convertir una fila de Postgres (Record) a dict para construir la entidad Interview.
def _row_to_interview(row: asyncpg.Record) -> Interview: # --> row es un asyncpg.Record; accedemos por clave de columna.
    """
    # Traduce columnas de DB a los campos de tu entidad Interview.
    # Si tu Interview tiene otros nombres (ej. candidate_id en lugar de id_candidate),
    # acá hacemos el "rename" para no romper el resto del código.
    """
    # "status" derivado (opcional): activo/completo
    status = "completed" if row["is_complete"] else ("active" if row["is_active"] else "inactive")
    data: Dict[str, Any] = {
        # Mapeo 1:1 con rename
        "id": row["id_interview"],                   # ← id <- id_interview
        "candidate_id": row["id_candidate"],         # ← candidate_id <- id_candidate
        "position_id": row["id_job"],                # ← position_id <- id_job  (si tu dominio usa "position")
        "user_id": row["id_user"],                   # ← opcional en tu entidad/response
        # Campos derivados/compatibles
        "status": status,                            # ← si tu entidad tiene "status"
        "created_at": row["timestamp_created"],      # ← created_at <- timestamp_created
        "updated_at": row["timestamp_created"],      # ← si no hay updated, reusamos created (o NULL)
        "scheduled_for": row["interview_start_time"],# ← scheduled_for <- interview_start_time
        "completed_at": None,                        # ← no hay en DB: lo dejamos None
        "questions": None,                           # ← no hay en DB: None (o [] si prefieres)
        "responses": None,                           # ← no hay en DB: None
    }
    return Interview(**{k: v for k, v in data.items() if v is not ...})


# Implementa la interfaz usada por tus use cases, pero con SQL real.
class PostgresInterviewRepository(InterviewRepository):
    def __init__(self) -> None:
        # Nada que abrir acá; el pool ya lo maneja Database.lifespan
        self._table = "interviews"  # --> Ajustar si se cambia el nombre de la tabla..

# Definición de CRUDS
# ==================================
# Métodos de lectura: get() y list()
# ==================================
    async def get(self, id: str) -> Optional[Interview]:
        sql = f"""
            SELECT
              id_interview, id_candidate, id_job, id_user,
              is_active, is_complete, interview_start_time, timestamp_created
            FROM {TABLE}
            WHERE id_interview = $1
            LIMIT 1
        """
        pool = Database.pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(sql, id)
        return _row_to_entity(row) if row else None

# LIST, lista toda la tabla. 
    async def list(self) -> List[Interview]:
        sql = f"""
            SELECT
              id_interview, id_candidate, id_job, id_user,
              is_active, is_complete, interview_start_time, timestamp_created
            FROM {TABLE}
            ORDER BY timestamp_created DESC
        """
        pool = Database.pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql)
        return [_row_to_entity(r) for r in rows]    


# =======================
# Crear (CREATE)
# =======================
    async def create(self, entity: Interview) -> Interview:
        sql = f"""
            INSERT INTO {TABLE} (
              id_interview, id_candidate, id_job, id_user,
              is_active, is_complete, interview_start_time, timestamp_created
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, COALESCE($8, now()))
            RETURNING
              id_interview, id_candidate, id_job, id_user,
              is_active, is_complete, interview_start_time, timestamp_created
        """
        pool = Database.pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                sql,
                # Map del dominio a DB:
                getattr(entity, "id", None),          # id_interview (o None si DB genera)
                getattr(entity, "candidate_id", None),# id_candidate
                getattr(entity, "position_id", None), # id_job
                getattr(entity, "user_id", None),     # id_user
                # flags de estado:
                True if getattr(entity, "status", "active") == "active" else False, # is_active
                True if getattr(entity, "status", "") == "completed" else False, # is_complete
                getattr(entity, "scheduled_for", None), # interview_start_time
                getattr(entity, "created_at", None),   # timestamp_created (opcional)
            )
        return _row_to_entity(row)

# =======================
# Actualizar (UPDATE)
# =======================
    async def update(self, id: str, entity: Interview) -> Optional[Interview]:
        is_active = True if getattr(entity, "status", "active") == "active" else False
        is_complete = True if getattr(entity, "status", "") == "completed" else False
        sql = f"""
            UPDATE {TABLE}
            SET
              id_candidate = COALESCE($2, id_candidate),
              id_job = COALESCE($3, id_job),
              id_user = COALESCE($4, id_user),
              is_active = $5,
              is_complete = $6,
              interview_start_time = COALESCE($7, interview_start_time)
            WHERE id_interview = $1
            RETURNING
              id_interview, id_candidate, id_job, id_user,
              is_active, is_complete, interview_start_time, timestamp_created
        """
        pool = Database.pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                sql,
                id,
                getattr(entity, "candidate_id", None),
                getattr(entity, "position_id", None),
                getattr(entity, "user_id", None),
                is_active,
                is_complete,
                getattr(entity, "scheduled_for", None),
            )
        return _row_to_entity(row) if row else None
    

# =======================
# Borrar (DELETE)
# =======================
    async def delete(self, id: str) -> bool:
        sql = f"DELETE FROM {TABLE} WHERE id_interview = $1"
        pool = Database.pool()
        async with pool.acquire() as conn:
            result = await conn.execute(sql, id)
        # Si asyncg devuelve algo como DELETE 1, hay que verificar porque afecto a la fila 1.
        return result.upper().startswith("DELETE 1")


    # ----------------------
    # Consultas auxiliares
    # ----------------------
    async def get_by_candidate(self, candidate_id: str) -> List[Interview]:
        sql = f"""
            SELECT
              id_interview, id_candidate, id_job, id_user,
              is_active, is_complete, interview_start_time, timestamp_created
            FROM {TABLE}
            WHERE id_candidate = $1
            ORDER BY timestamp_created DESC
        """
        pool = Database.pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, candidate_id)
        return [_row_to_entity(r) for r in rows]
  
    # position_id del dominio ↔ id_job en DB
    async def get_by_position(self, position_id: str) -> List[Interview]:
        sql = f"""
            SELECT
              id_interview, id_candidate, id_job, id_user,
              is_active, is_complete, interview_start_time, timestamp_created
            FROM {TABLE}
            WHERE id_job = $1
            ORDER BY timestamp_created DESC
        """
        pool = Database.pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(sql, position_id)
        return [_row_to_entity(r) for r in rows]

    # Traducimos el status de texto a flags booleanos.
    async def get_by_status(self, status: str) -> List[Interview]:
        
        want_complete = (status == "completed")
        want_active = (status == "active")
        sql = f"""
            SELECT
              id_interview, id_candidate, id_job, id_user,
              is_active, is_complete, interview_start_time, timestamp_created
            FROM {TABLE}
            WHERE
              ($1::bool IS NULL OR is_complete = $1) AND
              ($2::bool IS NULL OR is_active = $2)
            ORDER BY timestamp_created DESC
        """
        pool = Database.pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                sql,
                True if status in ("completed",) else None,  # filtra completed si aplica
                True if status in ("active", "inactive") else None  # filtra active si aplica
            )
        return [_row_to_entity(r) for r in rows]


