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
    LOGIN_USER: str = "{project_name}:login_user:{token}"
    RESET_PASSWORD: str = "{project_name}:reset_password:{token}"
    RESET_TOKEN_EXPIRE: int = 3600 * 24
    SECRET_KEY: str = "my_secret_key"
    ALGORITHM: str = "HS256"
    DOMAIN: str

    # postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "geotime"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "geotime"

    POSTGRES_HOST_TEST: str = "0.0.0.0"
    POSTGRES_PORT_TEST: int = 5432
    POSTGRES_USER_TEST: str = "postgres"
    POSTGRES_PASSWORD_TEST: str = "pass"
    POSTGRES_DB_TEST: str = "db"

    @property
    def DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def DATABASE_URL_TEST_psycopg(self):
        return f"postgresql+psycopg://{self.POSTGRES_USER_TEST}:{self.POSTGRES_PASSWORD_TEST}@{self.POSTGRES_HOST_TEST}:{self.POSTGRES_PORT_TEST}/{self.POSTGRES_DB_TEST}"

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
