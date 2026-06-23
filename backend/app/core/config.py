from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Security — SECRET_KEY must be set in .env (no insecure default)
    SECRET_KEY: str = ""

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_not_be_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("SECRET_KEY must be set in .env — refusing to start with an empty signing key")
        return v
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "sqlite:///./getfit.db"

    # Nutritionix API (optional — leave blank to use USDA fallback)
    NUTRITIONIX_APP_ID: str = ""
    NUTRITIONIX_API_KEY: str = ""

    # USDA FoodData Central API key (free at https://fdc.nal.usda.gov/api-guide.html)
    # DEMO_KEY works out of the box (30 req/hour, 50 req/day)
    USDA_API_KEY: str = "DEMO_KEY"

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",        # silently ignore unknown keys in .env
    )


settings = Settings()
