from pydantic import BaseModel, EmailStr, validator
from app.models.user import RegionEnum

#Esquemas de User

#Clase que define el esquema para la creacion de usuario.
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    region: RegionEnum #<- Esquema actualizado desde "team-setup"
    
    @validator("username") #<- Campo a validar
    def username_length(cls, v): #<- cls: clase modelo; v: valor del campo
        if len(v) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")
        return v

    @validator("password") #<- Campo a validar
    def password_strength(cls, v): #<- cls: clase modelo; v: valor del campo
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        return v

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
        
#Este esquema define cómo será la respuesta con el token
class Token(BaseModel):
    access_token: str
    token_type: str

#Se añadieron las funciones validator desde la rama "user-setup"