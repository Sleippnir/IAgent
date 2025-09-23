# Define los contratos de Entrada/Salida de la API para prompt (requests/responses).
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Clase para crear un prompt, con los campos minimos. 
class PromptCreate(BaseModel):
    desc_prompt: str

#  Todos opcionales para PATCH.
class PromptUpdate(BaseModel):
    desc_prompt: Optional[str] = None

# Clase que se encargará de devolver al cliente alinieado con nuestro adapter ROW+DICT.
class PromptResponse(BaseModel):
    id: str
    desc_prompt: str
    created_at: datetime

# Permite mapear desde objetos si luego usamos entidades.
    class Config:
        from_attributes = True
