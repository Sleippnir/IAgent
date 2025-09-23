# Define los contratos de Entrada/Salida de la API para jobs (requests/responses).
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Clase para crear un job, con los campos minimos. 
class JobCreate(BaseModel):
    job_role: str
    description: Optional[str] = None

#  Todos opcionales para PATCH.
class JobUpdate(BaseModel):
    job_role: Optional[str] = None
    description: Optional[str] = None

# Clase que se encargará de devolver al cliente alinieado con nuestro adapter ROW+DICT.
class JobResponse(BaseModel):
    id: str
    job_role: str
    description: Optional[str] = None
    created_at: datetime

# Permite mapear desde objetos si luego usamos entidades.
    class Config:
        from_attributes = True
