from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized app configuration, loaded from environment variables
    (and a local .env file during development).
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # CORS
    frontend_origin: str = "http://localhost:5173"

    # External services
    youtube_api_key: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    database_url: str = ""


settings = Settings()