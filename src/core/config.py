from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    rpc_url: str = Field(..., alias="RPC_URL")
    database_url: str = Field(..., alias="DATABASE_URL")
    retry_max_attempts: int = Field(5, alias="RETRY_MAX_ATTEMPTS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
