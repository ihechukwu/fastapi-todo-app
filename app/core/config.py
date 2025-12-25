from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTE: int
    REDIS_URL: str
    REFRESH_TOKEN_EXPIRE_DAYS: int

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # class Config:

    #     env_file = ".env"


settings = Settings()
