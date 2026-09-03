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
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    database_url: str = ""
    gemini_embedding_model: str = "gemini-embedding-001"


settings = Settings()