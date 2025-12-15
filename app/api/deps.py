# AD-OCV1/app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer # Đảm bảo đã import
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.crud.user_crud import user_crud

# SỬA 1: Cập nhật tokenUrl thành "/login" vì auth_router được mount tại root trong main.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login") 

def get_db_dep() -> Session:
    return next(get_db())

def get_current_user(
    # SỬA 2: Thêm Depends(oauth2_scheme) để FastAPI tự động lấy token từ header và kích hoạt Security
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
):
    """
    Lấy user hiện tại từ JWT.
    """
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload["sub"]
    user = user_crud.get_by_username(db, username)
    if not user or user.is_active != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or not found")
    return user