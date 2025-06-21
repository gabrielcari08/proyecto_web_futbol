from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.database import Base

class TournamentDate(Base):
    __tablename__ = "matchdays" 
    
    id = Column(Integer, primary_key=True)
    matchday_number = Column(Integer, nullable=False)  
    start = Column(DateTime, default=datetime.utcnow)
    end = Column(DateTime)
    is_closed = Column(Boolean, default=False)