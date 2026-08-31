from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized app configuration, loaded from environment variables
    (and a local .env file during development).
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # CORS
    frontend_origin: str = "http://localhost:5173"

    # Will be used starting Phase 2+ — defined now so the pattern is established
    youtube_api_key: str = ""
    openai_api_key: str = ""
    database_url: str = ""


settings = Settings()