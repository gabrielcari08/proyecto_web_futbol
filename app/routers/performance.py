from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import SessionLocal
from app.auth.dependency import get_current_user
from app.models.user import User
from app.models.performance import PlayerPerformance
from app.models.player import Player
from app.models.user_team import UserTeam
from app.models.team_player import UserTeamPlayer
from app.models.date import TournamentDate
from app.models.ranking import RegionalRanking
from app.schemas.performance import PerformanceResponse, LoadPerformance
from app.schemas.player import PosicionEnum

router = APIRouter(prefix="/performance", tags=["Performance"])

#Maneja la creacion de la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función que calcula los puntos según las reglas
def calculate_points(perf: LoadPerformance, player_position: PosicionEnum) -> int:
    #Inicializamos los puntos en 0
    points = 0

    #Goles y asistencias
    points += perf.goals * 5
    points += perf.assists * 3

    #Valla invicta solo si es arquero
    if perf.clean_sheet:
        if player_position == PosicionEnum.goalkeeper:
            points += 4
        else:
            raise HTTPException(status_code=400, detail="Solo los arqueros pueden tener valla invicta.")

    #MVP
    if perf.mvp:
        points += 8

    #Rating
    if 5.5 <= perf.rating < 6.5:
        points += 1
    elif 6.5 <= perf.rating < 7.5:
        points += 2
    elif 7.5 <= perf.rating < 8.5:
        points += 3
    elif 8.5 <= perf.rating < 9.5:
        points += 4
    elif perf.rating >= 9.5:
        points += 5

    #Penalizaciones
    points -= perf.yellow_cards * 1
    points -= perf.red_cards * 3
    
    return max(points, 0)

#Endpoint para cargar de forma manual el rendiemiento de cada jugador
@router.post("/load_performance", response_model=PerformanceResponse)
async def load_performance(performance_data: LoadPerformance,
                           db: Session = Depends(get_db)):
        
    #1. Verificar si ya existe un rendimiento para este jugador en esa fecha
    #Equivalente a: SELECT * 
    #               FROM performance 
    #               WHERE performance.player_id = [ID_DEL_JUGADOR] 
    #               AND performance.matchday_id = [ID_DE_LA_JORNADA] LIMIT 1;
    exists = db.query(PlayerPerformance).filter(
        PlayerPerformance.player_id == performance_data.player_id,
        PlayerPerformance.matchday_id == performance_data.matchday_id
        ).first()

    #Si existe un rendimiento lanzamos una excepcion
    if exists:
        raise HTTPException(status_code=400, detail="Ya existe una performance para este jugador en esta fecha.")

    #2. Obtener posición del jugador
    #Equivalente a: SELECT * FROM players WHERE player.id == [ID_DEL_JUGADOR] LIMIT 1;
    player = db.query(Player).filter(Player.id == performance_data.player_id).first()
    
    #Si no se encuentra el jugador
    if not player:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")

    #3. Calcular puntos
    total_points = calculate_points(performance_data, player.position)
    
    #4. Crear nuevo registro de rendimiento
    new_perf = PlayerPerformance(
        player_id = performance_data.player_id,
        matchday_id = performance_data.matchday_id,
        goals = performance_data.goals,
        assists = performance_data.assists,
        yellow_cards = performance_data.yellow_cards,
        red_cards = performance_data.red_cards,
        clean_sheet = performance_data.clean_sheet,
        mvp = performance_data.mvp,
        rating = performance_data.rating,
        points_earned = total_points
    )

    db.add(new_perf)
    db.commit()
    db.refresh(new_perf)

    return new_perf

#Endpoint para que el usuario pueda ver sus puntos obtenidos en cierta jornada.
@router.post("/calculate_team_points")
async def calculate_team_points(matchday: int,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    
    #1. Verificar que el equipo del usuario existe para "x" fecha
    #Equivalente a: SELECT * FROM user_teams 
    #               WHERE user_teams.id = [ID_DEL_USUARIO_ACTUAL] 
    #               AND user_teams.matchday_id = [ID_DE_LA_JORNADA] 
    #               LIMIT 1;
    user_team = db.query(UserTeam)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday)\
        .first()
        
    #Si el equipo no existe lanzamos una excepcion.
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No tienes un equipo creado para esta fecha")
        
    #2. Verificar que el equipo del usuario esta confirmado
    if not user_team.is_confirmed:
        raise HTTPException(status_code=400,
                            detail="El equipo no esta confirmado")
    
    #3. Verificar que la jornada esta cerrada
    #Equivalente a: SELECT * FROM matchday 
    #                       WHERE matchday.id = [matchday] AND matchday.is_closed = False 
    #                       LIMIT 1;
    is_closed = db.query(TournamentDate)\
        .filter(TournamentDate.id == matchday,
                TournamentDate.is_closed == False)\
        .first()
    
    #Si la jornada está abierta lanzamos una excepcion
    if is_closed:
        raise HTTPException(status_code=400,
                            detail="No se pueden calcular los puntos, la jornada no está cerrada")
        
    #4. Verificar que no se hayan calculado los puntos anteriormente.
    if user_team.total_points != 0:
        raise HTTPException(status_code=400,
                            detail="Los puntos ya han sido calculados anteriormente")
    
    #5. Obtener la suma de los puntos de cada jugador del equipo del usuario.
    #Equivalente a: SELECT sum(points_earned) FROM perfomances 
    #               JOIN players ON performances.player_id = players.id 
    #               JOIN user_team_players ON players.id = user_team_players.player_id 
    #               WHERE user_team_players.team_id = [ID_DEL_EQUIPO_DEL_USUARIO] 
    #               AND performances.matchday_id = [matchday] 
    total_points = db.query(func.sum(PlayerPerformance.points_earned))\
        .join(Player, PlayerPerformance.player_id == Player.id)\
        .join(UserTeamPlayer, Player.id == UserTeamPlayer.player_id)\
        .filter(UserTeamPlayer.team_id == user_team.id,
                PlayerPerformance.matchday_id == matchday)\
        .scalar() or 0
        
    #6. Duplicar los puntos del capitán.
    #Obtenemos el id del capitan dentro del equipo del usuario.
    #Equivalente a: SELECT * FROM performances
    #               JOIN players ON performances.player_id = players.id 
    #               JOIN user_teams ON players.id = user_teams.captain_id 
    #               WHERE user_teams.id = [ID_DEL_USUARIO_ACTUAL] 
    #               AND user_teams.matchday_id = [matchday] 
    #               LIMIT 1;
    captain = db.query(PlayerPerformance)\
        .join(Player, PlayerPerformance.player_id == Player.id)\
        .join(UserTeam, Player.id == UserTeam.captain_id)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday)\
        .first()
    
    #Al capitan le sumamos de nuevo sus puntos.
    if captain:
        total_points += captain.points_earned
        
    #7. Guardar los cambios
    user_team.total_points = total_points
    
    #8. Crear el registro para regional_rankings
    points_ranking = RegionalRanking(
        user_id = current_user.id,
        region = current_user.region,
        matchday_id = user_team.matchday_id,
        total_points = total_points
    )
    
    db.add(points_ranking)
    db.commit()
    db.refresh(user_team)         
    db.refresh(points_ranking)
    
    return {"message": "Puntos calculados exitosamente", "total_points": total_points}

#Endpoint para mostrar los puntos del usuario.
@router.get("/my_points")
async def my_points(matchday: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    
    #1. Verificar que el usuario tenga un equipo.
    #Equivalente a: SELECT * FROM user_teams 
    #               WHERE user_teams.user_id = [ID_DEL_USUARIO_ACTUAL] 
    #               AND user_teams.matchday_id = [matchday] 
    #               LIMIT 1;
    user_team = db.query(UserTeam)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday)\
        .first()
    
    #Si no se encontro el equipo, lanzamos una excepcion
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="Equipo no encontrado para esta fecha.")
    
    #Retornamos los puntos totales del usuario para esta fecha
    return {f"Puntos totales: {user_team.total_points}"}

#Endpoint para mostrar el rendimiento de los jugadores del equipo en una jornada especifica.
@router.get("/show_performance", response_model=list[PerformanceResponse])
async def show_performance(matchday: int,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    
    #1. Verificar que el usuario tenga un equipo.
    #Equivalente a: SELECT * FROM user_teams 
    #               WHERE user_teams.user_id = [ID_DEL_USUARIO_ACTUAL] 
    #               AND user_teams.matchday_id = [matchday] 
    #               LIMIT 1;
    user_team = db.query(UserTeam)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday)\
        .first()
    
    #Si no se encontro el equipo, lanzamos una excepcion
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="Equipo no encontrado para esta fecha.")
    
    #2. Verificar que el equipo del usuario esta confirmado
    if not user_team.is_confirmed:
        raise HTTPException(status_code=400,
                            detail="El equipo no esta confirmado")
    
    #3. Verificar que la jornada esta cerrada
    #Equivalente a: SELECT * FROM matchday 
    #               WHERE matchday.id = [matchday] AND matchday.is_closed = False 
    #               LIMIT 1;
    is_closed = db.query(TournamentDate)\
        .filter(TournamentDate.id == matchday,
                TournamentDate.is_closed == False)\
        .first()
    
    #Si la jornada está abierta lanzamos una excepcion
    if is_closed:
        raise HTTPException(status_code=400,
                            detail="No se puede realizar esta acción, la jornada no está cerrada")
        
    #4. Obtener el rendimiento de los jugadores del equipo del usuario.
    #Equivalente a: SELECT * FROM performances 
    #               JOIN players ON performances.player_id = players.id 
    #               JOIN user_team_players ON players.id = user_team_players.player_id 
    #               WHERE user_team_players.team_id = [ID_DEL_EQUIPO_DEL_USUARIO] 
    #               AND performances.matchday_id = [matchday]
    perf_players = db.query(PlayerPerformance)\
        .join(Player, PlayerPerformance.player_id == Player.id)\
        .join(UserTeamPlayer, Player.id == UserTeamPlayer.player_id)\
        .filter(UserTeamPlayer.team_id == user_team.id,
                PlayerPerformance.matchday_id == matchday)

        
    return perf_players
    
#Endpoint para mostrar el rendimiento de un jugador en una jornada especifica.
@router.get("/view_perf_player", response_model=list[PerformanceResponse])
async def view_perf_player(player_id: int,
                           matchday: int,
                           db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    
    #1. Verificar que el jugador existe.
    #Equivalente a: SELECT * FROM players WHERE player.id = [player_id]
    exists_player = db.query(Player).filter(Player.id == player_id).first()
    
    #Si no se encontro el jugador lanzamos una excepcion.
    if not exists_player:
        raise HTTPException(status_code=404,
                            detail="No se encontro un jugador con ese ID")
    
    #2. Verificar que la jornada existe.
    #Equivalente a: SELECT * FROM matchdays WHERE matchdays.id == [matchday]
    exists_matchday = db.query(TournamentDate).filter(TournamentDate.id == matchday).first()
    
    #Si no se encontro la jornada solicitada lanzamos una excepcion.
    if not exists_matchday:
        raise HTTPException(status_code=404,
                            detail="No se encontro la jornada")
        
    #3. Obtener el rendimiento del jugador en "x" jornada.
    #Equivalente a: SELECT * FROM performance 
    #               WHERE performance.player_id = [player_id] 
    #               AND performance.matchday_id = [matchday] 
    perf_player = db.query(PlayerPerformance)\
        .filter(PlayerPerformance.player_id == player_id,
                PlayerPerformance.matchday_id == matchday)\
        .all()

    return perf_player

#Endpoint para mostrar el rendimiento de los jugadores de un club en una jornada.
@router.get("/view_perf_club", response_model=list[PerformanceResponse])
async def view_perf_club(club: str,
                         matchday: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    
    #1. Verificar que el club solicitado existe.
    #Equivalente a: SELECT * FROM players WHERE players.club = [club]
    exists_club = db.query(Player).filter(Player.club == club)
    
    #Si no se encuentra el equipo lanzamos una excepcion.
    if not exists_club:
        raise HTTPException(status_code=404,
                            detail="No se encontro el club ingresado")
        
    #2. Verificar que la jornada existe
    #Equivalente a: SELECT * FROM matchdays WHERE matchdays.id == [matchday]
    exists_matchday = db.query(TournamentDate).filter(TournamentDate.id == matchday).first()
    
    #Si no se encontro la jornada solicitada lanzamos una excepcion.
    if not exists_matchday:
        raise HTTPException(status_code=404,
                            detail="No se encontro la jornada")
    
    #3. Obtenemos el rendimiento de los jugadores del club.
    #Equivalente a: SELECT * FROM performance
    #               JOIN players ON players.id = performance.player_id
    #               WHERE players.club = [club] 
    #               AND performance.matchday_id = [matchday]
    perf_club = db.query(PlayerPerformance)\
        .join(Player, PlayerPerformance.player_id == Player.id)\
        .filter(Player.club == club,
                PlayerPerformance.matchday_id == matchday)\
        .all()
        
    return perf_club