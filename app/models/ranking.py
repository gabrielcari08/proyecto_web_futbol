from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import declarative_base
from app.database import Base

class RegionalRanking(Base):
    __tablename__ = "regional_rankings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    region = Column(String, nullable=False)
    matchday_id = Column(Integer, ForeignKey("matchdays.id"))  
    total_points = Column(Integer, default=0)