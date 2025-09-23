# Define los contratos de Entrada/Salida de la API para users (requests/responses).
from pydantic import BaseModel, EmailStr, SecretStr
from typing import Optional
from datetime import datetime

# Clase para crear un user, con los campos minimos. 
class UserCreate(BaseModel):
    role_id: str                 
    name: str                    
    email: EmailStr              
    password: SecretStr          

# Clase para actualizar un user, con los campos minimos. 
class UserUpdate(BaseModel):
    role_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = None


class UserResponse(BaseModel):
    id: str
    role_id: str
    name: str
    email: EmailStr
    created_at: datetime
    
# Permite mapear desde objetos si luego usamos entidades.
    class Config:
        from_attributes = True

# ----- Roles -----
class RoleResponse(BaseModel):
    id: str
    role_name: str
    created_at: datetime

    class Config:
        from_attributes = True
