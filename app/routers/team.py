from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.schemas.team import TeamCreate, TeamResponse, FormationEnum
from app.schemas.player import AddPlayer, TeamPlayerResponse, PlayerResponse, PosicionEnum, ChooseCaptain
from app.models.user import User
from app.models.user_team import UserTeam
from app.models.player import Player
from app.models.team_player import UserTeamPlayer
from app.models.date import TournamentDate
from app.models.performance import PlayerPerformance
from app.models.performance import PlayerPerformance
from app.auth.dependency import get_current_user
from app.core.database import SessionLocal

router = APIRouter(prefix="/team", tags=["Team"])

#Endpoint de prueba
@router.get("/")
async def hello_router():
    return {"Hello": "Teams!"}

#Maneja la creacion de la sesion de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Diccionario de formaciones con posiciones requeridas
FORMATION_POSITIONS = {
    FormationEnum.f_4_4_2: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 4,
        PosicionEnum.midfielder: 4,
        PosicionEnum.forward: 2
    },
    FormationEnum.f_4_3_3: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 4,
        PosicionEnum.midfielder: 3,
        PosicionEnum.forward: 3
    },
    FormationEnum.f_4_2_3_1: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 4,
        PosicionEnum.midfielder: 5,  # 2 defensivos + 3 ofensivos
        PosicionEnum.forward: 1
    },
    FormationEnum.f_4_3_1_2: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 4,
        PosicionEnum.midfielder: 4,  # 3 centrales + 1 ofensivo
        PosicionEnum.forward: 2
    },
    FormationEnum.f_4_1_4_1: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 4,
        PosicionEnum.midfielder: 5,  # 1 defensivo + 4 centrales/ofensivos
        PosicionEnum.forward: 1
    },
    FormationEnum.f_3_5_2: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 3,
        PosicionEnum.midfielder: 5,
        PosicionEnum.forward: 2
    },
    FormationEnum.f_5_3_2: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 5,
        PosicionEnum.midfielder: 3,
        PosicionEnum.forward: 2
    },
    FormationEnum.f_4_4_1_1: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 4,
        PosicionEnum.midfielder: 4,
        PosicionEnum.forward: 2  # 1 segundo delantero + 1 delantero centro
    },
    FormationEnum.f_4_2_2_2: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 4,
        PosicionEnum.midfielder: 4,  # 2 defensivos + 2 ofensivos
        PosicionEnum.forward: 2
    },
    FormationEnum.f_4_5_1: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 4,
        PosicionEnum.midfielder: 5,
        PosicionEnum.forward: 1
    },
    FormationEnum.f_3_4_3: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 3,
        PosicionEnum.midfielder: 4,
        PosicionEnum.forward: 3
    },
    FormationEnum.f_5_4_1: {
        PosicionEnum.goalkeeper: 1,
        PosicionEnum.defender: 5,
        PosicionEnum.midfielder: 4,
        PosicionEnum.forward: 1
    }
}

#Funcion que devuelve el presupuesto disponible a usar para el usuario.
def calculate_team_budget(db: Session,
                          user_id: int,
                          matchday: int):

    #Finzalizamos la ejecucion de la funcion si matchday es 1
    if matchday <= 1:
        return 40.0

    #Incializamos team_budget en 40. Presupuesto base para todos los equipos.
    team_budget = 40.0

    #Obtenemos el numero de la jornada anterior.
    previous_matchday = matchday - 1

    #1. Obtenemos el equipo del usuario de una jornada anterior.
    user_team = db.query(UserTeam)\
        .filter(UserTeam.user_id == user_id,
                UserTeam.matchday_id == previous_matchday)\
        .first()

    #Si no se encontro un equipo lanzamos una excepcion.
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No se encontro un equipo.")

    #2. Contar cuantos jugadores con un rating igual o mayor a 8.5 hay.
    players_rating = db.query(UserTeamPlayer)\
        .join(Player, UserTeamPlayer.player_id == Player.id)\
        .join(PlayerPerformance, Player.id == PlayerPerformance.player_id)\
        .filter(UserTeamPlayer.team_id == user_team.id,
                PlayerPerformance.rating >= 8.5,
                PlayerPerformance.matchday_id == previous_matchday)\
        .count()        

    #3. Contar cuantos jugadores con MVP = True hay.
    players_mvp = db.query(UserTeamPlayer)\
        .join(Player, UserTeamPlayer.player_id == Player.id)\
        .join(PlayerPerformance, Player.id == PlayerPerformance.player_id)\
        .filter(UserTeamPlayer.team_id == user_team.id,
                PlayerPerformance.mvp == True,
                PlayerPerformance.matchday_id == previous_matchday)\
        .count() 

    #A players_rating lo multiplicamos por 0.5 (representa 0.5 millones)
    players_rating *= 0.5

    #A players_mvp lo multiplicamos por 3 (representa 3 millones)
    players_mvp *= 3

    #A final_budget ahora le asignamos el resultado de la suma. 
    final_budget = team_budget + players_mvp + players_rating

    #Retornamos final_budget -> el presupuesto disponible que puede usar cada usuario.
    return final_budget

#Funcion que valida que la posicion este en la formacion.
def validate_position_for_formation(db: Session,
                                    team_id: int,
                                    formation:FormationEnum,
                                    new_player_position: PosicionEnum) -> dict:
    
    #En formation_limits almacenamos la formacion elegida.
    formation_limits = FORMATION_POSITIONS[formation]
    #Resultado:
    #{
    #   PosicionEnum.goalkeeper: 1,
    #   PosicionEnum.defender: 4,
    #   PosicionEnum.midfielder: 3,
    #   PosicionEnum.forward: 3
    #},
    
    #Obtenemos la cuenta actual de cuantos jugadores hay en la posicion de new_player_position
    #Equivalente a: SELECT COUNT(*) 
    #               FROM user_team_players 
    #               JOIN players ON user_team_players.player_id = players.id 
    #               WHERE user_team_players.team_id = [team_id] AND players.position = [new_player_position]
    current_count = db.query(UserTeamPlayer)\
        .join(Player, UserTeamPlayer.player_id == Player.id)\
        .filter(
            UserTeamPlayer.team_id == team_id,
            Player.position == new_player_position
        )\
        .count()
    
    #max_allowed guarda el número máximo permitido para esa posición.
    #Por ej: max_allowed = formation_limits["PosicionEnum.defender"]
    #Resultado: 4
    max_allowed = formation_limits[new_player_position]
    
    #can_add devolvera un True o False
    can_add = current_count < max_allowed
    
    #Retornar toda la información necesaria en forma de diccionario.
    return {
        "can_add": can_add,
        "current_count": current_count,
        "max_allowed": max_allowed,
        "formation": formation,
        "position": new_player_position
    }

#Funcion que obtiene el equipo del usuario mas reciente por jornada activa
def get_user_team_for_active_matchday(db: Session, user_id: int):
    #Equivalente a: SELECT * 
    #               FROM user_teams 
    #               JOIN matchdays ON user_teams.matchday_id = matchdays.id 
    #               WHERE user_team.user_id = [ID_DEL_USUARIO_ACTUAL] 
    #               AND matchdays.is_closed = False
    #               ORDER BY start DESC LIMIT 1;
    return (
        db.query(UserTeam)
        .join(TournamentDate, UserTeam.matchday_id == TournamentDate.id)
        .filter(
            UserTeam.user_id == user_id,
            TournamentDate.is_closed == False  
        )
        .order_by(TournamentDate.start.desc()) 
        .first()
    )

#Endpoint para la creacion de un equipo.
@router.post("/create_team", response_model=TeamResponse)
async def create_team(team_data: TeamCreate,
                      current_user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    
    #1. Verificamos que hay una jorndada activa
    #Equivalente a: SELECT * FROM tournament_dates WHERE is_closed = false 
    #               ORDER BY matchday_number DESC LIMIT 1;
    matchday = db.query(TournamentDate)\
        .filter_by(is_closed=False)\
        .order_by(TournamentDate.matchday_number.desc()).first()

    #Si no hay ninguna jornada activa lanzamos una excepcion
    if not matchday:
        raise HTTPException(status_code=400, detail="No hay una jornada activa.")
    
    #2. Verificar que el usuario no haya creado ya un equipo para la fecha.
    #Equivalente a: SELECT * 
    #               FROM user_team 
    #               WHERE user_team.id == [ID_DEL USUARIO_ACTUAL] 
    #               AND user_team.id == matchday.id
    #               ORDER BY id DESC LIMIT 1;
    exists_team = db.query(UserTeam)\
    .filter(
        UserTeam.user_id == current_user.id,
        UserTeam.matchday_id == matchday.id
    )\
    .first()
    
    #Si se encontro un equipo del usuario para la fecha se lanza una excepcion.
    if exists_team:
        raise HTTPException(status_code=400,
                            detail="Ya has creado un equipo para esta fecha")

    #Creamos un nuevo equipo en UserTeam.
    new_team = UserTeam(
        user_id = current_user.id,
        matchday_id = matchday.id,
        formation = team_data.formation,
        budget_used = 0
    )
    
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    #Retornamos el equipo
    return new_team

#Endpoint para añadir jugadores al equipo.
@router.post("/add_player", response_model=PlayerResponse)
async def add_player(player_data: AddPlayer,
                     current_user: User = Depends(get_current_user),
                     db: Session = Depends(get_db)):    

    #1. Verificar si el jugador existe en la base de datos.
    #Equivalente a: SELECT * FROM players WHERE id = [player_data.id] LIMIT 1;
    exists_player = db.query(Player).filter(Player.id == player_data.id).first()
    
    #Si el jugador no existe o no se encuentra lanzamos una excepcion.
    if not exists_player:
        raise HTTPException(status_code=404,
                            detail="Jugador no encontrado en la base de datos.")
    
    #2. Obtenemos el equipo mas reciente del usuario por jornada activa mediante la funcion,
    user_team = get_user_team_for_active_matchday(db, current_user.id)
    
    #Si el usuario no creo ningun equipo:
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No se encontro un equipo para esta jornada")
    
    #3. Verificamos que el jugador a añadir no este en el equipo.
    #Equivalente a: SELECT * FROM user_player_teams 
    #               WHERE team_id = [user_team.id] AND player_id = [player_data.id] LIMIT 1;
    in_team = db.query(UserTeamPlayer).filter_by(team_id=user_team.id, player_id=player_data.id).first()
    
    #Si el jugador se encuentra en el equipo lanzamos una excepcion.
    if in_team:
        raise HTTPException(status_code=400,
                            detail="El jugador ya está en el equipo.")
    
    #4. Verificamos que no haya mas de 2 jugadores del mismo club en el equipo.
    #Equivalente a: SELECT COUNT(*) 
    #               FROM user_team_players 
    #               JOIN players ON user_team_players.player_id = players.id 
    #               WHERE user_team_players.team_id = [team_id] AND players.club = [club_del_jugador_nuevo]
    count_players = db.query(UserTeamPlayer)\
        .join(Player, UserTeamPlayer.player_id == Player.id)\
        .filter(
            UserTeamPlayer.team_id == user_team.id,
            Player.club == exists_player.club
        )\
        .count()
    
    #Si hay mas de 2 jugadores del mismo club en el equipo lanzamos una excepcion.
    if count_players >= 2:
        raise HTTPException(status_code=400,
                            detail=f"Ya hay 2 jugadores del mismo club en el equipo.")
        
    #5. Verificamos que la posicion del jugador coincida con la formacion.
    #"validation_result" contiene el diccionario que nos retorna "validate_position_for_formation"
    validation_result = validate_position_for_formation(
        db, user_team.id, user_team.formation, exists_player.position
    )
    
    if not validation_result["can_add"]:
        #Si can_add es False:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede añadir más jugadores en esta posición. "
                   f"Ya tienes {validation_result['current_count']}."
        )
        
    #6. Validar presupuesto
    
    #Calculamos el presupuesto disponible basado en el rendimiento anterior
    available_budget = calculate_team_budget(db, current_user.id, user_team.matchday_id)
    
    #En budget_used almacenamos la suma de players.value
    #Equivalente a: SELECT (SUM(players.value)
    #               FROM players 
    #               JOIN user_team_players ON players.id = user_team_players.player_id
    #               WHERE user_team_players.team_id = [user_team.id];
    budget_used = db.query(func.sum(Player.value))\
        .join(UserTeamPlayer, Player.id == UserTeamPlayer.player_id)\
        .filter(UserTeamPlayer.team_id == user_team.id)\
        .scalar() or 0
    
    #Si la suma entre el presupuesto usado y el valor del jugador a añadir supera los 45M
    #Lanzamos una excepcion.  
    if budget_used + exists_player.value > available_budget:
        raise HTTPException(status_code=400,
                            detail=f"Presupuesto superado. Disponible: {available_budget - budget_used}")
            
    #Creamos un nuevo jugador en user_team_players
    new_team_player = UserTeamPlayer(
        team_id = user_team.id,
        player_id = exists_player.id,
        position_on_field = exists_player.position
    )
    
    db.add(new_team_player)
    db.commit()
    db.refresh(new_team_player)
    
    #Retornamos el jugador añadido
    return exists_player

#Endpoint para escoger al capitan del equipo.
@router.post("/choose_captain")
async def choose_captain(captain_data: ChooseCaptain,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
        
    #1. Obtenemos el equipo mas reciente del usuario por jornada activa mediante la funcion,
    user_team = get_user_team_for_active_matchday(db, current_user.id)
    
    #Si el usuario no creo ningun equipo:
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No se encontro un equipo para esta jornada")
        
    #Si el equipo esta confirmado lanzamos una excepcion
    if user_team.is_confirmed:
        raise HTTPException(status_code=400,
                            detail="No se puede realizar esta acción porque el equipo ya está confirmado.")
        
    #2. Verificamos que el capitan este en el equipo.
    #Equivalente a: SELECT * FROM user_player_teams 
    #               WHERE team_id = [user_team.id] AND player_id = [player_data.id] LIMIT 1;
    in_team = db.query(UserTeamPlayer)\
        .filter_by(team_id=user_team.id, player_id=captain_data.captain_id).first()
    
    #Si el capitan no esta en el equipo lanzamos una excepcion.
    if not in_team:
        raise HTTPException(status_code=400,
                            detail="El jugador escogido como capitan no esta en el equipo.")
    
    #Asignamos el captain_id de captain_data al captain_id de user_team
    user_team.captain_id = captain_data.captain_id
    
    db.commit()
    db.refresh(user_team)
    
    #Retornamos un mensaje de exito si todo salio bien.
    return {"Jugador escogido como capitan correctamente"}

#Endpoint para eliminar un jugador del equipo
@router.delete("/remove_player/{player_id}")
async def delete_player(player_id: int,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
        
    #1. Obtenemos el equipo mas reciente del usuario por jornada activa mediante la funcion,
    user_team = get_user_team_for_active_matchday(db, current_user.id)
    
    #Si el usuario no creo ningun equipo:
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No se encontro un equipo para esta jornada")
        
    #Si el equipo del jugador esta confirmado, lanzar un excepcion.
    if user_team.is_confirmed:
        raise HTTPException(status_code=400,
                            detail="No se puede realizar esta acción porque el equipo ya está confirmado.")
    
    #2. Verificar que el jugador pertenece al equipo del usuario
    #Equivalente a: SELECT * 
    #               FROM user_team_players 
    #               JOIN user_teams ON user_team_players.team_id = user_teams.id 
    #               WHERE user_team_players.player_id = [ID_DEL_JUGADOR] 
    #               AND user_teams.user_id = [ID_DEL_USUARIO_ACTUAL] LIMIT 1;
    team_player = db.query(UserTeamPlayer)\
        .join(UserTeam, UserTeamPlayer.team_id == UserTeam.id)\
        .filter(
            UserTeamPlayer.player_id == player_id,
            UserTeam.user_id == current_user.id
        )\
        .first()

    #Si no se encuentra lanzamos una excepcion
    if not team_player:
        raise HTTPException(
            status_code=404,
            detail=f"Jugador no encontrado en tu equipo"
        )

    db.delete(team_player)
    db.commit()
    
    return {f"Jugador {player_id} eliminado correctamente"}

#Endpoint para que el usuario pueda ver su equipo actual
@router.get("/get_current_team")
async def get_current_team(db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    
    #1. Obtenemos el equipo mas reciente del usuario por jornada activa mediante la funcion,
    user_team = get_user_team_for_active_matchday(db, current_user.id)
    
    #Si el usuario no creo ningun equipo:
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No se encontro un equipo para esta jornada")

    #2. Obtener los jugadores del equipo
    #Equivalente a: SELECT * 
    #               FROM players 
    #               JOIN user_team_players ON players.id = user_team_players.player_id 
    #               WHERE user_team_players.team_id = [ID_DEL_EQUIPO_DEL_USUARIO]
    players_in_team = db.query(Player)\
        .join(UserTeamPlayer, Player.id == UserTeamPlayer.player_id)\
        .filter(UserTeamPlayer.team_id == user_team.id)\
        .all()

    #3. Obtener el jugador capitán si está asignado
    #Inicializamos captain como None, indicando que por defecto no hay capitan asignado
    captain = None
    #Verificamos que el equipo del usuario (user_team) tenga un capitan.
    if user_team.captain_id:
        #Si es True, entra a la consulta
        #Equivalente a: SELECT * 
        #               FROM players 
        #               WHERE players.id = [ID_DEL_CAPITAN_DEL_EQUIPO] LIMIT 1;
        captain = db.query(Player).filter(Player.id == user_team.captain_id).first()

    #4. Calcular presupuesto usado
    #Equivalente a: SELECT SUM(value)
    #               FROM players 
    #               JOIN user_team_players ON players.id = user_team_players.player_id 
    #               WHERE user_team_players.team_id = [ID_DEL_EQUIPO_DEL_USUARIO]
    budget_used = db.query(func.sum(Player.value))\
        .join(UserTeamPlayer, Player.id == UserTeamPlayer.player_id)\
        .filter(UserTeamPlayer.team_id == user_team.id)\
        .scalar() or 0.0

    #5. Preparar datos de respuesta
    return {
        "formation": user_team.formation,
        "is_confirmed": user_team.is_confirmed,
        "budget_used": budget_used,
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "club": p.club,
                "position": p.position,
                "value": p.value,
                "age": p.age,
                "sub_23": p.sub_23
            } for p in players_in_team
        ],
        "captain": {
            "id": captain.id,
            "name": captain.name,
            "position": captain.position,
            "club": captain.club
        } if captain else None
    }
     
#Endpoint para ver el equipo del usuario en determinada fecha.
@router.get("/view_team_in") #<- Ver equipo en...
async def view_team_in_matchday(matchday: int,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    
    #1. Obtener el equipo del usuario de "x" fecha
    #Equivalente a: SELECT * FROM user_teams 
    #               WHERE user_id = [ID_DEL_USUARIO_ACTUAL] 
    #               AND matchday_id = [matchday]
    #               LIMIT 1;
    user_team = db.query(UserTeam)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday)\
        .first()
        
    #Si no se encontro el equipo del usuario lanzamos una excepcion
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No se encontro un equipo.")
        
    #Si el equipo no esta confirmado, no puede verse, lanzamos excepcion
    if not user_team.is_confirmed:
        raise HTTPException(status_code=400,
                            detail="No se puede ver este equipo al no estar confirmado.")
        
    #2. Obtener los jugadores del equipo del usuario
    #Equivalente a: SELECT * FROM players 
    #               JOIN user_team_players ON players.id = user_team_players.player_id
    #               JOIN user_teams ON user_team_players.team_id = user_teams.id
    #               WHERE team_id = [ID_DEL_EQUIPO_DEL_USUARIO]
    players_in_team = db.query(Player)\
        .join(UserTeamPlayer, Player.id == UserTeamPlayer.player_id)\
        .join(UserTeam, UserTeamPlayer.team_id == UserTeam.id)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday)\
        .all()
        
    return {
        "formation": user_team.formation,
        "captain": user_team.captain_id,
        "is_confirmed": user_team.is_confirmed,
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "position": p.position,
                "club": p.club
            } for p in players_in_team
        ]
    }
     
#Endpoint para ver el equipo del usuario en determinada fecha.
@router.get("/view_team_in") #<- Ver equipo en...
async def view_team_in_matchday(matchday: int,
                                db: Session = Depends(get_db),
                                current_user: User = Depends(get_current_user)):
    
    #1. Obtener el equipo del usuario de "x" fecha
    #Equivalente a: SELECT * FROM user_teams 
    #               WHERE user_id = [ID_DEL_USUARIO_ACTUAL] 
    #               AND matchday_id = [matchday]
    #               LIMIT 1;
    user_team = db.query(UserTeam)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday)\
        .first()
        
    #Si no se encontro el equipo del usuario lanzamos una excepcion
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No se encontro un equipo.")
        
    #Si el equipo no esta confirmado, no puede verse, lanzamos excepcion
    if not user_team.is_confirmed:
        raise HTTPException(status_code=400,
                            detail="No se puede ver este equipo al no estar confirmado.")
        
    #2. Obtener los jugadores del equipo del usuario
    #Equivalente a: SELECT * FROM players 
    #               JOIN user_team_players ON players.id = user_team_players.player_id
    #               JOIN user_teams ON user_team_players.team_id = user_teams.id
    #               WHERE team_id = [ID_DEL_EQUIPO_DEL_USUARIO]
    players_in_team = db.query(Player)\
        .join(UserTeamPlayer, Player.id == UserTeamPlayer.player_id)\
        .join(UserTeam, UserTeamPlayer.team_id == UserTeam.id)\
        .filter(UserTeam.user_id == current_user.id,
                UserTeam.matchday_id == matchday)\
        .all()
        
    return {
        "formation": user_team.formation,
        "captain": user_team.captain_id,
        "is_confirmed": user_team.is_confirmed,
        "players": [
            {
                "id": p.id,
                "name": p.name,
                "position": p.position,
                "club": p.club
            } for p in players_in_team
        ]
    }

#Endpoint para confirmar el equipo
@router.post("/confirm_team")
async def confirm_team(db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    
    #1. Obtenemos el equipo mas reciente del usuario por jornada activa mediante la funcion,
    user_team = get_user_team_for_active_matchday(db, current_user.id)
    
    #Si el usuario no creo ningun equipo:
    if not user_team:
        raise HTTPException(status_code=404,
                            detail="No se encontro un equipo para esta jornada")
    
    #2. Verificar que el equipo no haya sido confirmado aún
    if user_team.is_confirmed:
        raise HTTPException(status_code=400, detail="Ya confirmaste este equipo.")
    
    #3. Verificar que haya exactamente 11 jugadores
    #Equivalente a: SELECT COUNT(*) FROM user_team_players WHERE team_id = user_team.id 
    total_players = db.query(UserTeamPlayer)\
        .filter_by(team_id=user_team.id)\
        .count()
    
    #Si el numero total de jugadores es distinto a 11 lanzamos una excepcion.
    if total_players != 11:
        raise HTTPException(status_code=400, detail=f"El equipo debe tener 11 jugadores. Actualmente tiene {total_players}.")
    
    #4. Verificar que haya al menos un sub-23
    #Equivalente a: SELECT COUNT(*) 
    #               FROM user_team_players 
    #               JOIN players ON user_team_player.player_id = players.id 
    #               WHERE user_team_players.team_id = user_teams.id AND players.sub_23 = True
    sub23_count = db.query(UserTeamPlayer)\
        .join(Player, UserTeamPlayer.player_id == Player.id)\
        .filter(
            UserTeamPlayer.team_id == user_team.id,
            Player.sub_23 == True
        ).count()
    
    #Si la cantidad de sub_23 en el equipo es menor a 1 lanzamos una excepcion
    if sub23_count < 1:
        raise HTTPException(status_code=400, detail="Debe haber al menos un jugador sub-23 en el equipo.")
    
    #5. Verificar que se haya asignado un capitán
    if user_team.captain_id is None:
        raise HTTPException(status_code=400, detail="Debes asignar un capitán antes de confirmar el equipo.")
    
    #6. Calcular el presupuesto del equipo
    #Equivalente a: SELECT sum(value) FROM players 
    #               JOIN user_team_players ON players.id = user_team_players.player_id 
    #               WHERE user_team_players.team_id = [ID_DEL_EQUIPO_DEL_USUARIO]
    total_budget_used = db.query(func.sum(Player.value)).\
        join(UserTeamPlayer, Player.id == UserTeamPlayer.player_id).\
        filter(UserTeamPlayer.team_id == user_team.id).\
        scalar() or 0.0
        
    user_team.budget_used = total_budget_used
    
    #7. Confirmar el equipo
    user_team.is_confirmed = True
    db.commit()

    return {f"Equipo confirmado correctamente. Tu valor de plantilla es de: {total_budget_used}"}