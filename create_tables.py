from app.models.user import User
from app.models.player import Player
from app.models.date import TournamentDate
from app.models.user_team import UserTeam
from app.models.performance import PlayerPerformance
from app.models.ranking import RegionalRanking
from app.models.team_player import UserTeamPlayer
from app.core.database import engine, Base

# Registrar modelos
Base.metadata.create_all(bind=engine)
