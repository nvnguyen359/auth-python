# CRUD camera
# app/api/routers/camera_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import schemas
from app.db.session import get_db
from app.services.camera_service import CameraService
from app.utils.response import response_success

router = APIRouter()
# --- ĐỊNH NGHĨA MODEL MỚI CHO RESPONSE DANH SÁCH (SỬA LỖI VALIDATION) ---


class CameraListResponse(BaseModel):
    """Mô hình Pydantic phản ánh cấu trúc trả về của response_success"""
    code: int = 200
    mes: str = "success"
    # Data phải là List[schemas.CameraOut]
    # Lưu ý: Bạn cần đảm bảo schemas.CameraOut đã được import đúng cách
    data: List[schemas.CameraOut]


@router.post("")
def create_camera(cam_in: schemas.CameraCreate, db: Session = Depends(get_db)):
    svc = CameraService(db)
    cam = svc.create_camera(cam_in)
    return response_success(data=cam)


@router.get("/{cam_id}")
def get_camera(cam_id: int, db: Session = Depends(get_db)):
    svc = CameraService(db)
    cam = svc.get_camera(cam_id)
    if not cam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return response_success(data=cam)


@router.get("", response_model=CameraListResponse, summary="Get all cameras")
def get_all_cameras(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    svc = CameraService(db)
    # Giả định CameraService có hàm get_all_cameras()
    cameras = svc.get_all_cameras(skip=skip, limit=limit)
    # response_success() sẽ bọc dữ liệu trong {code, mes, data}
    return response_success(data=cameras)


@router.patch("/{cam_id}")
def update_camera(cam_id: int, cam_in: schemas.CameraUpdate, db: Session = Depends(get_db)):
    svc = CameraService(db)
    cam = svc.update_camera(cam_id, cam_in)
    if not cam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return response_success(data=cam)


@router.post("/{cam_id}/connect")
def connect_camera(cam_id: int, db: Session = Depends(get_db)):
    svc = CameraService(db)
    cam = svc.connect_camera(cam_id)
    return response_success(data=cam)


@router.post("/{cam_id}/disconnect")
def disconnect_camera(cam_id: int, db: Session = Depends(get_db)):
    svc = CameraService(db)
    cam = svc.disconnect_camera(cam_id)
    return response_success(data=cam)
