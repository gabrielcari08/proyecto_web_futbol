from fastapi import APIRouter, Depends
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.schemas.player import PlayerResponse
from app.models.player import Player

router = APIRouter(prefix="/players", tags=["Players"])

#Maneja la creacion de la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Endpoint para listar todos los jugadores de la base de datos.
@router.get("/", response_model=list[PlayerResponse])
async def list_players(db: Session = Depends(get_db)):
    #Equivalente a SELECT * FROM players 
    players = db.query(Player).all()
    
    #Retorna todos los jugadores almacenados en la base de datos.
    return players