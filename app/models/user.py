from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.core.database import Base
import enum

class RegionEnum(str, enum.Enum):
    norte = "Norte"
    litoral = "Litoral"
    cuyo = "Cuyo"
    patagonia = "Patagonia"
    buenos_aires = "Buenos Aires"
    cordoba = "Córdoba"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)  # <- Nuevo campo obligatorio
    hashed_password = Column(String, nullable=False)
    region = Column(Enum(RegionEnum), nullable=False) # <- Se le agrega Enum a este campo.
    register_date = Column(DateTime, default=datetime.utcnow)
