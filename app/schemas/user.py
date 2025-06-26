from pydantic import BaseModel, EmailStr
from app.models.user import RegionEnum

#Esquemas de User

#Clase que define el esquema para la creacion de usuario.
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    region: RegionEnum #<- Ahora es de tip Enum

#Clase que define el esquema de lo que se le pedira a un usuario cuando inicie sesion.
class UserLogin(BaseModel):
    username: str
    password: str

#Clase que define el esquema la devolucion de usuario.
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
