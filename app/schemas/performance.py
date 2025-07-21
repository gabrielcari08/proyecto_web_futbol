from pydantic import BaseModel

#Esquema de rendimiento

#Clase que define el esquema de respuesta del rendimiento del jugador
class PerformanceResponse(BaseModel):
    player_id: int
    matchday_id: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    clean_sheet: bool
    mvp: bool
    rating: float
    
    points_earned: float
    
    class Config:
        orm_mode = True

#Clase que define el esquema para cargar las estadisticas de un jugador
class LoadPerformance(BaseModel):
    player_id: int
    matchday_id: int
    goals: int
    assists: int
    yellow_cards: int
    red_cards: int
    clean_sheet: bool
    mvp: bool
    rating: float
    