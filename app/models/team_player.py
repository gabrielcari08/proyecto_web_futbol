from sqlalchemy import Column, Integer, ForeignKey, Boolean, String
from sqlalchemy.orm import declarative_base
from app.database import Base

class UserTeamPlayer(Base):
    __tablename__ = "user_team_players"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("user_teams.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    position_on_field = Column(String, nullable=False)  # Ej: "Defensor", "Arquero"
