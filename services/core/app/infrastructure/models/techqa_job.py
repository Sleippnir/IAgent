# Define los contratos de Entrada/Salida de la API para "technical questions answers jobs" (requests/responses).
from pydantic import BaseModel
from typing import List
from datetime import datetime

# Clase para crear un vinculo "technical questions answers jobs", con los campos minimos. 
class TechQAJobLink(BaseModel):
    job_id: str
    techqa_id: str


class TechQAJobLinkResponse(BaseModel):
    job_id: str
    techqa_id: str
    created_at: datetime

# Permite mapear desde objetos si luego usamos entidades.
    class Config:
        from_attributes = True
