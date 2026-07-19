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

    # CORS / Frontend
    # FRONTEND_URL is the deployed frontend origin (used for email links AND CORS).
    FRONTEND_URL: str = "http://localhost:5173"
    # Extra allowed CORS origins, comma-separated (e.g. a preview URL). Optional.
    CORS_ORIGINS: str = ""

    @property
    def cors_origins(self) -> list[str]:
        origins = {
            "http://localhost:5173",
            "http://localhost:3000",
            self.FRONTEND_URL.rstrip("/"),
        }
        origins.update(
            o.strip().rstrip("/") for o in self.CORS_ORIGINS.split(",") if o.strip()
        )
        return [o for o in origins if o]

    # Email (Gmail SMTP) — used for account-confirmation / set-password links.
    # Leave SMTP_USER/SMTP_PASS blank in dev to log the link instead of sending.
    # SMTP_PASS must be a Gmail *App Password* (16 chars), not the account password.
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_FROM: str = ""          # defaults to SMTP_USER if blank
    EMAIL_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # set-password link validity (24h)

    # Google SSO — public OAuth Client ID (no secret needed for ID-token flow)
    GOOGLE_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",        # silently ignore unknown keys in .env
    )


settings = Settings()
