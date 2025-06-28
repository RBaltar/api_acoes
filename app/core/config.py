from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    API_SAFE_MODE: bool = True
    DATA_MAX_AGE_MINUTES: int = 5
    RATE_LIMIT_PER_MINUTE: int = 20

    class Config:
        env_file = ".env"

settings = Settings()