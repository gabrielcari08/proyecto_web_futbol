from pydantic import BaseModel
from enum import Enum

#Esquema de jugador

class PosicionEnum(str, Enum):
    goalkeeper = "Arquero"
    defender = "Defensor"
    midfielder = "Mediocampista"
    forward = "Delantero"
    
#Clase que define el esquema de respuesta cuando se añade un jugador
class PlayerResponse(BaseModel):
    id: int
    name: str
    club: str
    position: PosicionEnum
    value: float
    age: int
    sub_23: bool

    class Config:
        orm_mode = True
        
#Clase que define el esquema de respuesta cuando se enlisten los jugadores del equipo de un usuario
class TeamPlayerResponse(BaseModel):
    name: str
    club: str
    position: PosicionEnum
    value: float
    
    class Config:
        orm_mode = True

#Clase que define el esquema para añadir un jugador a un equipo
class AddPlayer(BaseModel):
    id: int
    #position: PosicionEnum #<- Eliminamos campo posicion.
  
#Clase que define el esquema para escoger un capitan  
class ChooseCaptain(BaseModel):
    captain_id: int