from pydantic import BaseModel
from enum import Enum 
from typing import Optional

#Esquema de equipo

class FormationEnum(str, Enum):
    f_4_4_2 = "4-4-2"
    f_4_3_3 = "4-3-3"
    f_4_2_3_1 = "4-2-3-1"
    f_4_3_1_2 = "4-3-1-2"
    f_4_1_4_1 = "4-1-4-1"
    f_3_5_2 = "3-5-2"
    f_5_3_2 = "5-3-2"
    f_4_4_1_1 = "4-4-1-1"
    f_4_2_2_2 = "4-2-2-2"
    f_4_5_1 = "4-5-1"
    f_3_4_3 = "3-4-3"
    f_5_4_1 = "5-4-1"
    
#Clase que define el esquema para crear un equipo
class TeamCreate(BaseModel):
    formation: FormationEnum

#Clase que define el esquema de respuesta cuando se cree el equipo
class TeamResponse(BaseModel):
    id: int
    formation: FormationEnum
    captain_id:  Optional[int] = None
    matchday_id: int
    budget_used: float
    
    class Config:
        orm_mode = True

