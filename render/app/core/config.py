from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Skylark BI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Supabase
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase anon/public key")
    SUPABASE_SERVICE_KEY: str = Field("", description="Supabase service_role key for admin ops")

    # Monday.com
    MONDAY_API_KEY: str = Field(..., description="Monday.com API token")
    MONDAY_API_URL: str = "https://api.monday.com/v2"

    # Hugging Face
    HF_API_KEY: str = ""
    HF_MODEL: str = "HuggingFaceH4/zephyr-7b-beta"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8501","https://skylark-business-agent.vercel.app"]

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "case_sensitive": True}


@lru_cache
def get_settings() -> Settings:
    return Settings()
