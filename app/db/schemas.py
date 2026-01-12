# Pydantic schemas cho request/response
# app/db/schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# =========================
# USER SCHEMAS
# =========================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: str = Field(default="operator",
                      pattern="^(admin|supervisor|operator)$")
    is_active: int = 1


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(admin|supervisor|operator)$")
    is_active: Optional[int] = None


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        # Cập nhật cho Pydantic v1. Dùng from_attributes=True cho Pydantic v2
        from_attributes = True


# =========================
# CAMERA SCHEMAS
# =========================

class CameraBase(BaseModel):
    # --- CÁC TRƯỜNG BỔ SUNG ĐỂ KHỚP VỚI LOGIC UPSERT ---
    # Logic service cung cấp 'name' từ v4l2-ctl/OpenCV
    name: Optional[str] = None 
    status: Optional[str] = Field(None, pattern="^(ACTIVE|DISCONNECTED|ERROR)$")
    os_index: Optional[int] = None
    # --------------------------------------------------

    device_id: str = Field(..., min_length=3, max_length=100)
    display_name: Optional[str] = None
    unique_id:Optional[str] = None
    rtsp_url: Optional[str] = None
    backend: Optional[str] = None
    prefer_gst: int = 0
    is_connected: int = 0
    device_path: Optional[str] = None


class CameraCreate(CameraBase):
    # Khai báo lại các trường bắt buộc (NOT NULL trong models.py)
    device_id: str = Field(..., min_length=3, max_length=100)
    unique_id: str = Field(...) 


class CameraUpdate(BaseModel):
    display_name: Optional[str] = None
    rtsp_url: Optional[str] = None
    backend: Optional[str] = None
    prefer_gst: Optional[int] = None
    is_connected: Optional[int] = None
    device_path: Optional[str] = None
    unique_id:Optional[str] = None
    
    # Bổ sung các trường cần cập nhật
    name: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(ACTIVE|DISCONNECTED|ERROR)$")
    os_index: Optional[int] = None


class CameraOut(CameraBase):
    id: int
    created_at: datetime
    
    class Config:
        # Pydantic v2 style
        from_attributes = True


# =========================
# ORDER SCHEMAS
# =========================

class OrderBase(BaseModel):
    camera_id: Optional[int] = None
    user_id: Optional[int] = None
    parent_id: Optional[int] = None
    session_id: Optional[str] = None
    code: Optional[str] = None
    status: str = Field(default="packing", pattern="^(packing|closed|error)$")
    path_avatar: Optional[str] = None
    path_video: Optional[str] = None
    order_metadata: Optional[str] = None
    note: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(packing|closed|error)$")
    path_avatar: Optional[str] = None
    path_video: Optional[str] = None
    order_metadata: Optional[str] = None
    note: Optional[str] = None
    closed_at: Optional[datetime] = None


class OrderOut(OrderBase):
    id: int
    created_at: datetime
    start_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None

    class Config:
        from_attributes = True