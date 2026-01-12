# app/core/config.py

import os
import json 
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Server config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # Database
    DB_URL: str

    # JWT config (CHỮ IN HOA)
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 6000

    # Logging
    LOG_LEVEL: str = "info"
    OPENCV_LOG_LEVEL: str = "OFF"
    OPENCV_VIDEOIO_PRIORITY_MSMF: int = 0

    # Pagination defaults
    DEFAULT_PAGE: int = 0
    DEFAULT_PAGE_SIZE: int = 100
    MAX_PAGE_SIZE: int = 1500

    # CORS origins
    ALLOWED_ORIGINS: Union[List[str], str] = []

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.strip().startswith("["):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return []
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

# Khởi tạo settings ở cuối file
settings = Settings()