from pydantic import BaseModel
from app.models.user import RegionEnum

#Esquemas de rankings

#Clase que define el esquema de respuesta de un ranking.
class RankingResponse(BaseModel):
    user_id: int
    region: RegionEnum
    matchday_id: int
    total_points: int