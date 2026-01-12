# app/services/camera_service.py
from sqlalchemy.orm import Session
from app.crud.camera_crud import camera_crud
from app.db import schemas


class CameraService:
    def __init__(self, db: Session):
        self.db = db

    def create_camera(self, cam_in: schemas.CameraCreate):
        return camera_crud.create(self.db, cam_in)

    def get_camera(self, cam_id: int):
        return camera_crud.get(self.db, cam_id)

    def get_all_cameras(self, skip: int = 0, limit: int = 100):
        """
        Lấy danh sách tất cả camera, gọi đến tầng CRUD.
        """
        return camera_crud.get_all(self.db, skip=skip, limit=limit)

    def update_camera(self, cam_id: int, cam_in: schemas.CameraUpdate):
        db_cam = camera_crud.get(self.db, cam_id)
        if not db_cam:
            return None
        return camera_crud.update(self.db, db_cam, cam_in)

    def connect_camera(self, cam_id: int):
        return camera_crud.connect(self.db, cam_id)

    def disconnect_camera(self, cam_id: int):
        return camera_crud.disconnect(self.db, cam_id)

    def delete_camera(self, cam_id: int):
        """
        Xóa camera theo ID.
        """
        return camera_crud.delete_by_id(self.db, cam_id)

    def delete_all_cameras(self) -> int:
        """
        Xóa toàn bộ camera trong hệ thống.
        Trả về số lượng bản ghi đã xóa.
        """
        return camera_crud.delete_all(self.db)
