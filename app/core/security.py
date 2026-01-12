# app/core/security.py

from datetime import datetime, timedelta
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

# Cấu hình hash password
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu có khớp không"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash mật khẩu để lưu vào DB"""
    return pwd_context.hash(password)

# --- SỬA LỖI: Tạo alias (tên khác) cho hàm get_password_hash ---
# Giúp code cũ gọi hash_password vẫn chạy bình thường
hash_password = get_password_hash 

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Tạo JWT Token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Lưu ý: ACCESS_TOKEN_EXPIRE_MINUTES phải viết hoa theo config mới
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Giải mã JWT Token để lấy thông tin user"""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None