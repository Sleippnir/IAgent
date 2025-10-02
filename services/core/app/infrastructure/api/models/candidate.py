# Define los contratos de Entrada/Salida de la API para candidates (requests/responses).
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Clase para crear un candidato, con los campos minimos. (lo que NO tiene defaults en DB).
class CandidateCreate(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    phone_num: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume: Optional[bytes] = None 

#  Todos opcionales para PATCH/PUT parcial.
class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_num: Optional[str] = None
    linkedin_url: Optional[str] = None
    resume: Optional[bytes] = None

# Clase que se encargará de devolver al cliente alinieado con nuestro adapter ROW+DICT.
class CandidateResponse(BaseModel):
    id: str
    name: str
    last_name: str
    email: EmailStr
    phone_num: Optional[str] = None
    linkedin_url: Optional[str] = None
    created_at: datetime

# permite mapear desde objetos si luego usamos entidades
    class Config:
        from_attributes = True  
