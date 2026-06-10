from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Security — SECRET_KEY must be set in .env (no insecure default)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "sqlite:///./getfit.db"

    # Nutritionix API (optional — leave blank to use mock data)
    NUTRITIONIX_APP_ID: str = ""
    NUTRITIONIX_API_KEY: str = ""

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",        # silently ignore unknown keys in .env
    )


settings = Settings()
