from sqlalchemy import Column, Integer, Float, ForeignKey, String, UniqueConstraint, Enum, Boolean
from sqlalchemy.orm import declarative_base
from app.core.database import Base
import enum

class FormationEnum(str, enum.Enum):
    f_4_4_2 = "4-4-2"
    f_4_3_3 = "4-3-3"
    f_4_2_3_1 = "4-2-3-1"
    f_4_3_1_2 = "4-3-1-2"
    f_4_1_4_1 = "4-1-4-1"
    f_3_5_2 = "3-5-2"
    f_5_3_2 = "5-3-2"
    f_4_4_1_1 = "4-4-1-1"
    f_4_2_2_2 = "4-2-2-2"
    f_4_5_1 = "4-5-1"
    f_3_4_3 = "3-4-3"
    f_5_4_1 = "5-4-1"

class UserTeam(Base):
    __tablename__ = "user_teams"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    matchday_id = Column(Integer, ForeignKey("matchdays.id")) 
    formation = Column(Enum(FormationEnum), nullable=False) #<- Modificamos este campo y lo hacemos Enum
    budget_used = Column(Float, nullable=False)
    captain_id = Column(Integer, ForeignKey("players.id"))
    total_points = Column(Integer, default=0)
    is_confirmed = Column(Boolean, default=False) #<- Añadimos este campo desde "team-setup"
    
    __table_args__ = (
        UniqueConstraint('user_id', 'matchday_id', name='unique_team_per_user_matchday'),
    )
    
#Notas:

#-Añadimos el campo is_confirmed a este modelo desde la rama "team-setup" y no desde "db-setup" porque
#era un cambio pequeño que no demandaria mucho tiempo. 
#Ademas estamos trabajando en algo extenso y no podiamos hacer commit de nada aun como para
#trasladarnos hacia la rama "db-setup"