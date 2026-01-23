from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Interview Assistant Pro"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./interview_assistant.db"

    # Auth
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_MONTHLY: str = ""  # $29/month
    STRIPE_PRICE_ID_YEARLY: str = ""   # $249/year

    # Anthropic (your master API key)
    ANTHROPIC_API_KEY: str = ""

    # Usage limits
    FREE_TIER_QUESTIONS_PER_MONTH: int = 50
    PRO_TIER_QUESTIONS_PER_MONTH: int = 10000

    # CORS
    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def database_url_async(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # SQLite URLs already have the correct format (sqlite+aiosqlite://)
        return url

    class Config:
        env_file = ".env"


settings = Settings()
