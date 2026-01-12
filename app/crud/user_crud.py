from sqlalchemy.orm import Session
from app.db import models, schemas
from app.crud.base import CRUDBase
from app.core.security import hash_password 

class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):
    
    def get_by_username(self, db: Session, username: str):
        return db.query(self.model).filter(self.model.username == username).first()

    def create(self, db: Session, obj_in: schemas.UserCreate) -> models.User:
        # Chuyển schema thành dict
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, "model_dump") else obj_in.dict()
        
        # Lấy password thô ra để hash
        raw_password = obj_in_data.pop("password")
        
        # Chỉ hash DUY NHẤT một lần ở đây
        # Đảm bảo password_hash là tên cột trong DB của bạn
        obj_in_data["password_hash"] = hash_password(raw_password)
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def activate(self, db: Session, user_id: int):
        user = self.get(db, id=user_id)
        if user:
            user.is_active = 1
            db.commit()
            db.refresh(user)
        return user

    def deactivate(self, db: Session, user_id: int):
        user = self.get(db, id=user_id)
        if user:
            user.is_active = 0
            db.commit()
            db.refresh(user)
        return user

user_crud = CRUDUser(models.User)