from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)  # <- Nuevo campo obligatorio
    hashed_password = Column(String, nullable=False)
    region = Column(String, nullable=False)
    register_date = Column(DateTime, default=datetime.utcnow)
