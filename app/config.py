from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, EmailStr, Field


ENV_PATH = Path(__file__).resolve().parent / ".env"


class DatabaseSettings(BaseModel):
    host: str
    user: str
    password: str
    db: str
    port: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    debug: bool = False
    gmail: EmailStr
    pass_evn: str
    gemini_api_key: str
    port: int
    ngrok_authtoken: str
    firm_name: str
    accountant_email: EmailStr
    database: DatabaseSettings

settings = Settings() # pyright: ignore[reportCallIssue] -> since it warns about a wrong thing here


