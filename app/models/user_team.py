from sqlalchemy import Column, Integer, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from app.core.database import Base

class UserTeam(Base):
    __tablename__ = "user_teams"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    matchday_id = Column(Integer, ForeignKey("matchdays.id")) 
    formation = Column(String, nullable=False)
    budget_used = Column(Float, nullable=False)
    captain_id = Column(Integer, ForeignKey("players.id"))
    total_points = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'matchday_id', name='unique_team_per_user_matchday'),
    )