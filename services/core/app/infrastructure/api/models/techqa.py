# Define los contratos de Entrada/Salida de la API para "techincal questions answers" (requests/responses).
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Clase para crear un "techincal questions answers", con los campos minimos. 
class TechQACreate(BaseModel):
    question: str
    answer: str

#  Todos opcionales para PATCH.
class TechQAUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

# Clase que se encargará de devolver al cliente alinieado con nuestro adapter ROW+DICT.
class TechQAResponse(BaseModel):
    id: str
    question: str
    answer: str
    created_at: datetime

# Permite mapear desde objetos si luego usamos entidades.
    class Config:
        from_attributes = True
