from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "PromptlyDrawn"
    ENVIRONMENT: Literal["dev", "prod"] = "dev"
    DEBUG: bool = True

    DATABASE_URL: str
    CELERY_BROKER_URL: str

    model_config = SettingsConfigDict(env_file=".env.backend")


settings = Settings()
