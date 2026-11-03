from typing import Union
from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "API Biblioteca SENA"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Base de datos
    DATABASE_URL: str = "postgresql+psycopg://didi_web_user:EewKgdL1ronaEnJwPPxnsPOB8J9gBrnw@dpg-dbkuml6k1f9s73e25v20-a.virginia-postgres.render.com/didi_web"
    TEST_DATABASE_URL: str = "postgresql+psycopg://didi_web_user:EewKgdL1ronaEnJwPPxnsPOB8J9gBrnw@dpg-dbkuml6k1f9s73e25v20-a.virginia-postgres.render.com/didi_web"

    # Seguridad y JWT
    SECRET_KEY: str = "cambiar_clave_secreta_minimo_32_caracteres_hex_000"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: Union[list[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000"
    ]

    @field_validator("SECRET_KEY")
    @classmethod
    def validar_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[list[str], str]) -> list[str]:
        if isinstance(v, str):
            import json
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (ValueError, TypeError):
                pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

