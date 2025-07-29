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
@router.get("/region")
async def ranking_region(region: RegionEnum,
                         db: Session = Depends(get_db)):

    #Obtenemos los puntos totales de los usuarios de determinada region
    #Equivalente a: SELECT user_id, SUM(total_points) as user_team_points
    #               FROM regional_rankings 
    #               WHERE region = [region] 
    #               GROUP BY user_id 
    #               ORDER BY user_team_points DESC
    regional_ranking = db.query(RegionalRanking.user_id,
                               func.sum(RegionalRanking.total_points).label('tm'))\
        .filter(RegionalRanking.region == region)\
        .group_by(RegionalRanking.user_id)\
        .order_by(func.sum(RegionalRanking.total_points).desc())\
        .all()
        
    return [
        {
            "user_id": user_id,
            "region": region,
            "total_points": total_points
        } for user_id, total_points in regional_ranking
    ] 
    
#Endpoint para ver el ranking de forma general.
@router.get("/general")
async def ranking_general(db: Session = Depends(get_db)):
    
    #Obtenemos los puntos totales de los usuarios de forma general.
    #Equivalente a: SELECT user_id, SUM(total_points) as user_team_points
    #               FROM regional_rankings 
    #               GROUP BY user_id 
    #               ORDER BY user_team_points DESC
    regional_ranking = db.query(RegionalRanking.user_id,
                               func.sum(RegionalRanking.total_points).label('tm'))\
        .group_by(RegionalRanking.user_id)\
        .order_by(func.sum(RegionalRanking.total_points).desc())\
        .all()
        
    return [
        {
            "user_id": user_id,
            "total_points": total_points
        } for user_id, total_points in regional_ranking
    ] 
    
#Endpoint para que el usuario pueda ver su posicion en el ranking.
@router.get("/my_position")
async def my_position(db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    
    #1. Obtenemos los puntos del usuario.
    #Equivalente a: SELECT SUM(total_points) FROM regional_ranking 
    #               WHERE user_id = [user_id] 
    user_points = db.query(func.sum(RegionalRanking.total_points))\
        .filter(RegionalRanking.user_id == current_user.id)\
        .scalar() or 0
    
    #Lanzamos una excepcion si no se encuantra nada. 
    if user_points == 0:
        raise HTTPException(status_code=404,
                        detail="No tienes posición en el ranking. Debes crear un equipo.")
    
    #2. Obtenemos la posicion del usuario en el ranking general.
    #Equivalente a: SELECT COUNT(*) FROM (
        #           SELECT user_id FROM regional_rankings 
        #           GROUP BY user_id 
        #           HAVING SUM(total_points) > [user_points]) 
    user_general_position = db.query(RegionalRanking.user_id)\
        .group_by(RegionalRanking.user_id)\
        .having(func.sum(RegionalRanking.total_points) > user_points)\
        .count() 
      
    #3. Obtenemos la posicion del usuario en el ranking regional.
    #Equivalente a: SELECT COUNT(*) FROM (
        #           SELECT user_id FROM regional_rankings 
        #           WHERE region = [region]
        #           GROUP BY user_id 
        #           HAVING SUM(total_points) > [user_points])
    user_regional_position = db.query(RegionalRanking.user_id)\
        .filter(RegionalRanking.region == current_user.region)\
        .group_by(RegionalRanking.user_id)\
        .having(func.sum(RegionalRanking.total_points) > user_points)\
        .count() 
        
    return {"General": f"Te encuentras en la posicion: {user_general_position + 1}. " 
            f"Con un total de: {user_points} puntos. ",
            "Regional": f"Te encuentras en la posicion: {user_regional_position + 1}. " 
            f"Con la misma cantidad de puntos ({user_points})."}
    