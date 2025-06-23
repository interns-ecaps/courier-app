# common/config.py
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str
    db_user: str
    db_pass: str
    db_host: str
    db_name: str
    db_port: int
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 2

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()

class LoginRequest(BaseModel):
    username: str
    password: str
