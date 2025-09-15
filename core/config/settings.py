from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    alz_db_path: str = Field(default="data/app.db", alias="ALZ_DB_PATH")

settings = Settings()
