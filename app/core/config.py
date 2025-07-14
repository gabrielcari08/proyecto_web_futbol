# Cambio de pydantic_settings
from pydantic_settings import BaseSettings
# Por: pydantic

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    
    secret_key: str
    algorithm: str = "HS256"
    
    #Minutos para que el token expire
    access_token_expire_minutes: int = 30
    
    jwt_audience: str = "titulares-app"

    class Config:
        env_file = ".env"

settings = Settings()
