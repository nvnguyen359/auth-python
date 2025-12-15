# app/crud/user_crud.py
from sqlalchemy.orm import Session
from app.db import models, schemas
from app.crud.base import CRUDBase

class CRUDUser(CRUDBase[models.User, schemas.UserCreate, schemas.UserUpdate]):
    """
    CRUD cho User, kế thừa từ CRUDBase.
    Thêm các hàm đặc thù: get_by_username, activate/deactivate.
    """

    def get_by_username(self, db: Session, username: str):
        return db.query(self.model).filter(self.model.username == username).first()

    def activate(self, db: Session, user_id: int):
        user = self.get(db, user_id)
        if user:
            user.is_active = 1
            db.commit()
            db.refresh(user)
        return user

    def deactivate(self, db: Session, user_id: int):
        user = self.get(db, user_id)
        if user:
            user.is_active = 0
            db.commit()
            db.refresh(user)
        return user

user_crud = CRUDUser(models.User)
