"""
Central app configuration, loaded from environment variables /.env file.
Using pydantic-settings so misconfigured env vars fail fast at startup
instead of silently breaking a request later.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GEMINI_API_KEY: str # <- changed this
    SECRET_KEY: str = "codecoach-gemini-api"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week
    DATABASE_URL: str = "sqlite:///./codecoach.db"

    # Comma-separated list, e.g. "https://codecoach.vercel.app,https://www.codecoach.app"
    # Defaults to "*" for local dev; set this explicitly before deploying anywhere public.
    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()