# Define los contratos de Entrada/Salida de la API para generalqa (requests/responses).
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Clase para crear un generalqa, con los campos minimos. 
class GeneralQACreate(BaseModel):
    question: str
    answer: str

#  Todos opcionales para PATCH.
class GeneralQAUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None

# Clase que se encargará de devolver al cliente alinieado con nuestro adapter ROW+DICT.
class GeneralQAResponse(BaseModel):
    id: str
    question: str
    answer: str
    created_at: datetime

# Permite mapear desde objetos si luego usamos entidades.
    class Config:
        from_attributes = True
