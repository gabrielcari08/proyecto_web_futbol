from pydantic import BaseSettings

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: str = "5432"

    class Config:
        env_file = ".env"

settings = Settings()
