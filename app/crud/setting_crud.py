# app/crud/setting_crud.py
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.db.models import Setting
from pydantic import BaseModel

# Schema tối giản để khớp với CRUDBase
class SettingSchema(BaseModel):
    key: str
    value: str

class CRUDSetting(CRUDBase[Setting, SettingSchema, SettingSchema]):
    def upsert_by_key(self, db: Session, key: str, value: str):
        # Kiểm tra tồn tại
        db_obj = db.query(self.model).filter(self.model.key == key).first()
        
        if db_obj:
            # Nếu có thì update
            db_obj.value = value
        else:
            # Nếu chưa có thì tạo mới
            db_obj = self.model(key=key, value=value)
            db.add(db_obj)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj

setting_crud = CRUDSetting(Setting)