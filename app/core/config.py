from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from dotenv import load_dotenv
from typing import List, Any
import os
import json # Cần import json cho logic parse

load_dotenv()

class Settings(BaseSettings):
    # Cấu hình file .env
    # Sử dụng env_file và extra="ignore" là phong cách Pydantic V2
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Server (Giữ lại os.getenv để linh hoạt)
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    reload: bool = os.getenv("RELOAD", "True").lower() == "true"

    # Database (Giữ lại os.getenv để linh hoạt)
    db_url: str = os.getenv("DB_URL", "sqlite:///./app/db/adocv1.db")

    # JWT (Giữ lại os.getenv để linh hoạt)
    jwt_secret: str = os.getenv("JWT_SECRET", "changeme")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    # Logging (Giữ lại os.getenv để linh hoạt)
    log_level: str = os.getenv("LOG_LEVEL", "info")

    # Pagination (Giữ lại os.getenv để linh hoạt)
    default_page: int = int(os.getenv("DEFAULT_PAGE", 0))
    default_page_size: int = int(os.getenv("DEFAULT_PAGE_SIZE", 100))
    max_page_size: int = int(os.getenv("MAX_PAGE_SIZE", 500))

    # CORS
    # SỬA LỖI: Thay đổi type hint từ List[str] thành Any để tránh Pydantic tự parse trước
    allowed_origins: Any = Field(default_factory=list)

    @field_validator("allowed_origins", mode="before")
    def parse_allowed_origins(cls, v: Any) -> List[str]:
        # Env có thể trả về:
        # - CSV string: "http://a,http://b"
        # - JSON array: ["http://a","http://b"]
        # - "*" hoặc rỗng
        if v is None:
            return []
        if isinstance(v, list):
            return [s.strip() for s in v if isinstance(s, str) and s.strip()]
        if isinstance(v, str):
            s = v.strip()
            if s == "" or s == "*":
                return []
            # thử parse JSON array nếu có dạng bắt đầu bằng '['
            if s.startswith("[") and s.endswith("]"):
                try:
                    arr = json.loads(s)
                    if isinstance(arr, list):
                        return [str(i).strip() for i in arr if str(i).strip()]
                except Exception:
                    # fallback xuống CSV nếu JSON lỗi
                    pass
            # CSV fallback
            return [i.strip() for i in s.split(",") if i.strip()]
        # fallback an toàn
        return []

settings = Settings()