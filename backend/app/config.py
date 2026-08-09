from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.5"
    database_url: str = "sqlite:///./devopsmentor.db"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
