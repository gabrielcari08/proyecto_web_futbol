from fastapi import APIRouter, Depends, HTTPException
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.schemas.player import PlayerResponse, PosicionEnum
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

#Endpoint para filtrar todos aquellos jugadores sub-23
@router.get("/sub-23", response_model=list[PlayerResponse])
async def list_players_sub_23(db: Session = Depends(get_db)):
    #Equivalente a: SELECT * FROM players WHERE sub_23 = True
    players_sub_23 = db.query(Player).filter(Player.sub_23 == True).all()
    
    #Retorna todos aquellos jugadores que sean sub-23
    return players_sub_23

#Endpoint para filtrar todos aquellos jugadores de "x" club
@router.get("/club", response_model=list[PlayerResponse])
async def list_players_for_club(club: str,
                                db: Session = Depends(get_db)):
    #Equivalente a: SELECT * FROM players WHERE players.club = 'River Plate' (o el club que sea)
    players_club = db.query(Player).filter(Player.club == club).all()
    
    #Si no se encuentra el club ingresado, lanzamos una excepcion
    if not players_club:
        raise HTTPException(status_code=404,
                            detail="No se encontraron jugadores o equipo inexistente")
    
    #Retornamos todos aquellos jugadores que sean de ese club
    return players_club

@router.get("/position", response_model=list[PlayerResponse])
async def list_players_for_position(position: PosicionEnum,
                                    db: Session = Depends(get_db)):
    
    #Equivalente a: SELECT * FROM players WHERE players.position = 'defender' (o la posicion que sea)
    players_position = db.query(Player).filter(Player.position == position).all()
        
    #Retorna todos aquellos jugadores que sean de esa posicion
    return players_position