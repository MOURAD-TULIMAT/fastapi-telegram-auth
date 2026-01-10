from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_ignore_empty=True,
        extra="allow",
        )

    TOKEN_HASH_PEPPER: str = ""

    APP_NAME: str = "FastAPI Telegram Auth"
    API_PREFIX: str = "/v1"
    CORS_ORIGINS: str | None = None

    DATABASE_URL: str = "mysql+aiomysql://user:pass@127.0.0.1:3306/authdb"

    INACTIVE_OVERWRITE_AFTER_SECONDS: int = 300
    ACTIVATION_TOKEN_TTL_MINUTES: int = 15
    TELEGRAM_BOT_USERNAME: str = ""
    ENVIRONMENT: str = "dev"
settings = Settings()
