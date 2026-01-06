from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True,
        extra="allow",
        )

    APP_NAME: str = "FastAPI Telegram Auth"
    API_PREFIX: str = "/v1"
    CORS_ORIGINS: str | None = None

    DATABASE_URL: str = "mysql+aiomysql://user:pass@127.0.0.1:3306/authdb"

settings = Settings()
