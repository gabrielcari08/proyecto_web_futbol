from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.auth.dependency import get_current_user
from app.models.ranking import RegionalRanking
from app.models.user import User, RegionEnum
from app.models.date import TournamentDate
from app.schemas.ranking import RankingResponse

router = APIRouter(prefix="/ranking", tags=["Ranking"])

#Maneja la creacion de la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Endpoint para ver el raking de determinada region.
@router.get("/region", response_model=list[RankingResponse])
async def ranking_region(region: RegionEnum,
                         db: Session = Depends(get_db)):
    
    #1. Obtenemos la jornada cerrada mas reciente.
    #Equivalente a: SELECT * FROM matchdays 
    #               WHERE is_closed = True 
    #               ORDER BY start DESC 
    #               LIMIT 1;
    matchday = db.query(TournamentDate)\
        .filter(TournamentDate.is_closed == True)\
        .order_by(TournamentDate.start.desc())\
        .first()
    
    #2. Obtener el ranking de determinada region.
    #Equivalente a: SELECT * FROM regional_rankings 
    #               WHERE regional_rankings.region = [region]
    #               AND matchday_id = [matchday]
    #               ORDER BY total_points DESC
    region_ranking = db.query(RegionalRanking)\
        .filter(RegionalRanking.region == region,
                RegionalRanking.matchday_id == matchday.id)\
        .order_by(RegionalRanking.total_points.desc())\
        .all()
        
    return region_ranking

#Endpoint para ver el ranking de forma general.
@router.get("/general", response_model=list[RankingResponse])
async def ranking_general(db: Session = Depends(get_db)):
    
    #1. Obtenemos la jornada cerrada mas reciente.
    #Equivalente a: SELECT * FROM matchdays 
    #               WHERE is_closed = True 
    #               ORDER BY start DESC 
    #               LIMIT 1;
    matchday = db.query(TournamentDate)\
        .filter(TournamentDate.is_closed == True)\
        .order_by(TournamentDate.start.desc())\
        .first()
    
    #2. Obtener el ranking general.
    #Equivalente a: SELECT * FROM regional_rankings 
    #               WHERE matchday_id = [matchday]
    #               ORDER BY total_points DESC
    ranking_in_general = db.query(RegionalRanking)\
        .filter(RegionalRanking.matchday_id == matchday.id)\
        .order_by(RegionalRanking.total_points.desc())\
        .all()
        
    return ranking_in_general 

#Endpoint para que el usuario pueda ver su posicion en el ranking.
@router.get("/my_position")
async def my_position(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    
    #1. Obtenemos la jornada cerrada mas reciente.
    #Equivalente a: SELECT * FROM matchdays 
    #               WHERE is_closed = True 
    #               ORDER BY start DESC 
    #               LIMIT 1;
    matchday = db.query(TournamentDate)\
        .filter(TournamentDate.is_closed == True)\
        .order_by(TournamentDate.start.desc())\
        .first()
    
    #2. Obtenemos los puntos del usuario.
    #Equivalente a: SELECT total_points FROM regional_ranking 
    #               WHERE user_id = [user_id] 
    #               AND matchday_id = [matchday]
    user_points = db.query(RegionalRanking.total_points)\
        .filter(RegionalRanking.user_id == current_user.id,
                RegionalRanking.matchday_id == matchday.id)\
        .scalar() or 0
    
    #Lanzamos una excepcion si no se encuantra nada. 
    if user_points is None:
        raise HTTPException(status_code=404,
                        detail="No tienes posición en el ranking. Debes crear un equipo.")
    
    #3. Obtenemos la posicion del usuario en el ranking general.
    #Equivalente a: SELECT COUNT(id) FROM regional_ranking 
    #               WHERE total_points > [user_points]
    #               AND matchday_id = [matchday]
    user_general_position = db.query(func.count(RegionalRanking.id))\
        .filter(RegionalRanking.total_points > user_points,
                RegionalRanking.matchday_id == matchday.id)\
        .scalar() or 0
      
    #4. Obtenemos la posicion del usuario en el ranking regional.
    #Equivalente a: SELECT COUNT(id) FROM regional_ranking 
    #               WHERE total_points > [user_points]
    #               AND matchday_id = [matchday]
    user_regional_position = db.query(func.count(RegionalRanking.id))\
        .filter(RegionalRanking.total_points > user_points,
                RegionalRanking.region == current_user.region,
                RegionalRanking.matchday_id == matchday.id)\
        .scalar() or 0
        
    return {"General": f"Te encuentras en la posicion: {user_general_position + 1}. " 
            f"Con un total de: {user_points} puntos. ",
            "Regional": f"Te encuentras en la posicion: {user_regional_position + 1}. " 
            f"Con la misma cantidad de puntos ({user_points})."}
    