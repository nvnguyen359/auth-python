# JWT, Argon2 password hashing, role check 
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.hash import argon2
from app.core.config import settings

def hash_password(password: str) -> str:
    return argon2.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    try:
        return argon2.verify(password, password_hash)
    except Exception:
        return False

def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    """
    Tạo JWT Token. 
    Hỗ trợ tham số expires_delta (timedelta) để khớp với auth_router.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Mặc định lấy từ config nếu không truyền vào
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
