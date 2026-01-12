# app/api/routers/setting_router.py
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.db.session import get_db
from app.crud.setting_crud import setting_crud
from app.utils.response import response_success

router = APIRouter(prefix="/settings", tags=["settings"])

@router.post("/sync")
def sync_settings(
    payload: Dict[str, Any] = Body(...), # Nhận JSON dynamic (key: value)
    db: Session = Depends(get_db)
):
    results = []
    # Duyệt qua từng field trong JSON
    for key, value in payload.items():
        # Gọi logic upsert
        # Chuyển value sang string để đồng bộ kiểu dữ liệu TEXT trong DB
        db_setting = setting_crud.upsert_by_key(db, key=key, value=str(value))
        results.append({db_setting.key: db_setting.value})

    return response_success(
        data=results, 
        message="Settings synced successfully"
    )

@router.get("")
def get_all_settings(db: Session = Depends(get_db)):
    settings = setting_crud.get_multi(db)
    # Chuyển list object thành dict đơn giản
    data = {s.key: s.value for s in settings}
    return response_success(data=data)