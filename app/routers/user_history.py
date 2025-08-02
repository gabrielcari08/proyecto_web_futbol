from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.auth.dependency import get_current_user
from app.models.user import User
from app.models.player import Player
from app.models.team_player import UserTeamPlayer
from app.models.user_team import UserTeam
from app.models.ranking import RegionalRanking

router = APIRouter(prefix="/history", tags=["User-History"])


#Maneja la creacion de la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
#Endpoint que devuelve un resumen de lo que fue la jornada del usuario
#Cuantos puntos hizo y en que posicion del ranking quedó
@router.get("/user_matchdays")
async def user_matchdays(matchday: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    
    #1. Obtener cuantos puntos hizo en la jornada solicitada.
    #Equivalente a: SELECT * FROM user_teams 
    #               WHERE user_teams.user_id = [ID_DEL_USUARIO_ACTUAL] 
    #               AND user_teams.matchday_id = [matchday] 
    #               AND user_teams.is_confirmed = True  
    #               LIMIT 1;  
    user_points_earned = db.query(UserTeam)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday,
                UserTeam.is_confirmed == True)\
        .first()
    
    if not user_points_earned:
        raise HTTPException(status_code=404,
                            detail="No se encontraron datos para esta jornada.")
        
    #2. Obtenemos el lugar en el ranking general
    #Equivalente a: SELECT COUNT(*) FROM regional_rankings 
    #               WHERE regional_rankings.total_points > [PUNTOS_DEL_USUARIO]
    general_user_position = db.query(RegionalRanking)\
        .filter(RegionalRanking.total_points > user_points_earned.total_points)\
        .count()
        
    #3. Obtenemos el lugar en el ranking regional
    #Equivalente a: SELECT COUNT(*) FROM regional_rankings 
    #               WHERE regional_rankings.total_points > [PUNTOS_DEL_USUARIO] 
    #               AND regional_rankigs.region = [REGION_DEL_USUARIO_ACTUAL]
    regional_user_position = db.query(RegionalRanking)\
        .filter(RegionalRanking.total_points > user_points_earned.total_points, 
                RegionalRanking.region == current_user.region)\
        .count()
        
    return {
        "message": f"En la jornada {matchday}: Obtuviste {user_points_earned.total_points} puntos. "
                f"Finalizaste en la posición {general_user_position + 1} en forma general "
                f"y {regional_user_position + 1} en tu región."
    }
    
#Se puede añadir a futuro:
#Endpoint que muestra la evolucion de presupuesto del usuario.

#Validaciones: solo se puede ver el historial de jornadas cerradas.
