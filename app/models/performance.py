from sqlalchemy import Column, Integer, Boolean, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from app.core.database import Base

class PlayerPerformance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    matchday_id = Column(Integer, ForeignKey("matchdays.id"))  
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    clean_sheet = Column(Boolean, default=False) #"Valla invicta"
    mvp = Column(Boolean, default=False) 
    rating = Column(Float, default=0.0)

    points_earned = Column(Integer, default=0)  #"Puntos obtenidos"