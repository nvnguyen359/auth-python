# AD-OCV1/app/api/routers/auth_router.py

from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

# --- Import Core Components ---
from app.api import deps
from app.db.session import get_db
from app.crud.user_crud import user_crud
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.utils.response import response_success
from app.db import schemas

# --- Định nghĩa Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

router = APIRouter()

@router.post(
    "/api/login",
    response_model=Token,
    summary="User login (OAuth2 Form)",
    tags=["auth"]
)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
) -> Any:
    """
    Xác thực người dùng bằng username và password (form data).
    Trả về JWT Access Token chuẩn OAuth2.
    """
    # 1. Tìm kiếm user
    user = user_crud.get_by_username(db, form_data.username)
    
    # 2. Kiểm tra điều kiện (Tồn tại, Mật khẩu, Active)
    if not user or user.is_active != 1:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 3. Tạo Access Token
    # Lưu ý: Đảm bảo file app/core/security.py đã được cập nhật để nhận expires_delta
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=user.username,
        expires_delta=access_token_expires
    )
    
    # 4. Trả về response chuẩn OAuth2 (QUAN TRỌNG)
    # Trả về trực tiếp dict khớp với response_model=Token
    # Không dùng response_success ở đây để tránh lỗi validation và lỗi Swagger UI
    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get(
    "/me",
    # Lưu ý: Nếu response_success trả về cấu trúc {code, data, mes} 
    # thì response_model này có thể gây lỗi validation nếu schemas.UserOut không khớp.
    # Nếu gặp lỗi ở endpoint này, hãy tạm thời bỏ response_model hoặc cập nhật schema.
    response_model=schemas.UserOut, 
    summary="Get current user information",
    tags=["auth"]
)
def read_users_me(
    current_user: schemas.UserOut = Depends(deps.get_current_user)
) -> Any:
    """
    Lấy thông tin user hiện tại.
    """
    # SỬA LỖI: Dùng tham số 'mes' thay vì 'message'
    return response_success(
        data=current_user,
        mes="User information retrieved successfully"
    )