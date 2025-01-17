from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

load_dotenv()
BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    ENV: str = "local"
    PROJECT_NAME: str = "geotime"
    VERSION: str = "0.0.1"
    PREFIX: str = "/api"
    DEFAULT_TIMEZONE: str = "Europe/Moscow"
    DOMAIN: str

    ADMIN_PASSWORD: str
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6666

    # Celery
    CELERY_BROKER: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/11"
    CELERY_BACKEND: str = f"redis://{REDIS_HOST}:{REDIS_PORT}/12"
    BROKER_QUEUE_NAME_PREFIX: str = "broker_sender_queue_"
    CLOSE_RECEIPT_QUEUE_NAME: str = "close_receipt_queue"
    DEFAULT_QUEUE_NAME: str = "default"

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
