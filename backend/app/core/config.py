from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "Lexis"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        url = url.replace("sslmode=require", "ssl=require")
        return url

    # Neo4j
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # JWT Authentication
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Gemini Config
    GEMINI_API_KEY: str = ""
    GEMINI_API_KEYS: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Storage Config
    # STORAGE_BACKEND selects the StorageProvider implementation ("local" | "s3"...).
    STORAGE_BACKEND: str = "local"
    STORAGE_LOCAL_DIR: str = "uploads"
    # The extracted text lives in source_chunks, so the original upload is not
    # needed after a successful build. Delete it by default; flip on only if you
    # add re-ingestion or user re-download.
    KEEP_SOURCE_FILE: bool = False

    model_config = SettingsConfigDict(
        env_file=(".env.test", ".env"), env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
