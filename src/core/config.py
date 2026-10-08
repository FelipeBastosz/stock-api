from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Stock Management API"
    DATABASE_URL: str = "postgresql+asyncpg://admin:admin_password@localhost:5432/estoque_db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()