from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres-user:user-password@localhost:port_number/database_name"
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60
    MATCH_THRESHOLD: float = 0.8
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # ── SMTP Email ─────────────────────────────────────────────────────────────
    # Set SMTP_ENABLED=true and fill in credentials to activate email dispatch.
    # Gmail  : SMTP_HOST=smtp.gmail.com, SMTP_PORT=587, use an App Password.
    # SendGrid: SMTP_HOST=smtp.sendgrid.net, SMTP_PORT=587,
    #           SMTP_USERNAME=apikey, SMTP_PASSWORD=<your SendGrid API key>.
    SMTP_ENABLED: bool = False
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""   # sender email / SendGrid literal "apikey"
    SMTP_PASSWORD: str = ""   # Gmail App Password or SendGrid API key

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Singleton — import this everywhere
settings = Settings()
