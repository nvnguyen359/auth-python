# Nghiệp vụ user 
# app/services/user_service.py
from sqlalchemy.orm import Session
from app.crud.user_crud import user_crud
from app.db import schemas

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_in: schemas.UserCreate):
        return user_crud.create(self.db, user_in)

    def get_user(self, user_id: int):
        return user_crud.get(self.db, user_id)

    def get_by_username(self, username: str):
        return user_crud.get_by_username(self.db, username)

    def update_user(self, user_id: int, user_in: schemas.UserUpdate):
        db_user = user_crud.get(self.db, user_id)
        if not db_user:
            return None
        return user_crud.update(self.db, db_user, user_in)

    def activate_user(self, user_id: int):
        return user_crud.activate(self.db, user_id)

    def deactivate_user(self, user_id: int):
        return user_crud.deactivate(self.db, user_id)
