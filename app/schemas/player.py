# app/schemas/player.py
from pydantic import BaseModel
from enum import Enum

class PosicionEnum(str, Enum):
    goalkeeper = "Arquero"
    defender = "Defensor"
    midfielder = "Mediocampista"
    forward = "Delantero"

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
