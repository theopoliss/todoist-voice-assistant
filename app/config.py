from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    todoist_api_token: str
    openai_api_key: str
    model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()