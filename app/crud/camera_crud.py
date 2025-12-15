# app/crud/camera_crud.py

from typing import List, Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from app.db import models, schemas
from app.crud.base import CRUDBase

class CRUDCamera(CRUDBase[models.Camera, schemas.CameraCreate, schemas.CameraUpdate]):
    """
    CRUD cho Camera, kế thừa từ CRUDBase.
    Thêm các hàm đặc thù: connect/disconnect, upsert.
    """
    
    def get_by_device_id(self, db: Session, device_id: str) -> Optional[models.Camera]:
        """
        Tìm camera dựa trên ID duy nhất của thiết bị.
        Dùng device_id vì cột này là UNIQUE trong models.Camera.
        """
        return db.query(self.model).filter(self.model.device_id == device_id).first()

    def upsert(self, db: Session, obj_in: Dict[str, Any]) -> models.Camera:
        """
        Thao tác tạo mới hoặc cập nhật dựa trên 'device_id'.
        - Nếu tìm thấy theo device_id, cập nhật các trường.
        - Nếu không tìm thấy, tạo mới.
        """
        device_id = obj_in.get("device_id")
        if not device_id:
            raise ValueError("Dictionary must contain 'device_id' for upsert operation.")
            
        db_obj = self.get_by_device_id(db, device_id)

        if db_obj:
            # Cập nhật đối tượng đã có
            update_data = obj_in.copy()
            
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    # Cập nhật giá trị
                    setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        else:
            # --- FIX: Chuyển dict thành Pydantic Model trước khi gọi create ---
            # CRUDBase.create yêu cầu obj_in phải có phương thức .dict()
            camera_create_model = schemas.CameraCreate(**obj_in)
            return self.create(db, obj_in=camera_create_model)

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Camera]:
        """
        Lấy tất cả camera (có phân trang tùy chọn)
        """
        return self.get_multi(db, skip=skip, limit=limit)
        
    def connect(self, db: Session, camera_id: int):
        cam = self.get(db, camera_id)
        if cam:
            cam.is_connected = 1
            cam.status = "ACTIVE"
            db.commit()
            db.refresh(cam)
        return cam

    def disconnect(self, db: Session, camera_id: int):
        cam = self.get(db, camera_id)
        if cam:
            cam.is_connected = 0
            cam.status = "DISCONNECTED"
            db.commit()
            db.refresh(cam)
        return cam

camera_crud = CRUDCamera(models.Camera)