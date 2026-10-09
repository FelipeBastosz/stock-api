from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Variedades - API de Controle de Estoque"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para controle de inventário, produtos, fornecedores e movimentações de estoque."
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    DATABASE_URL: str = "postgresql+asyncpg://admin:admin_password@localhost:5432/estoque_db"
    DATABASE_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()