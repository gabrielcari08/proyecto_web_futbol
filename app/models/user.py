from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String, unique=True, nullable=False)
    contraseña_hash = Column(String, nullable=False)
    region = Column(String, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
