from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str
    db_user: str
    db_pass: str
    db_host: str
    db_name: str
    db_port: str

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
