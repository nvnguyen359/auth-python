import os
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

    # JWT config
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
    # Khai báo Union để chấp nhận cả chuỗi CSV từ .env hoặc List
    ALLOWED_ORIGINS: Union[List[str], str] = []

    # Xử lý chuỗi CSV (comma-separated) thành List Python thực thụ
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            return v
        return []

    # Cấu hình để đọc file .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore" # Bỏ qua các biến thừa nếu có
    )

# Khởi tạo instance settings để dùng ở nơi khác
settings = Settings()

# --- Phần này chỉ để test khi chạy trực tiếp file này ---
if __name__ == "__main__":
    print(f"Server running at: {settings.HOST}:{settings.PORT}")
    print(f"Database URL: {settings.DB_URL}")
    print(f"CORS Origins ({len(settings.ALLOWED_ORIGINS)} domains):")
    for origin in settings.ALLOWED_ORIGINS:
        print(f" - {origin}")