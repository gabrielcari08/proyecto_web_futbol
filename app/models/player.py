from sqlalchemy import Column, Integer, String, Float, Boolean, Enum
import enum
from app.core.database import Base

class PosicionEnum(str, enum.Enum):
    goalkeeper = "Arquero"
    defender = "Defensor"
    midfielder = "Mediocampista"
    forward = "Delantero"

class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    club = Column(String, nullable=False)
    position = Column(Enum(PosicionEnum), nullable=False)
    value = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    sub_23 = Column(Boolean, default=False)