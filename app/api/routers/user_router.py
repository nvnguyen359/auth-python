# CRUD user 
# app/api/routers/user_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import schemas
from app.db.session import get_db
from app.services.user_service import UserService
from app.core.security import hash_password
from app.utils.response import response_success

router = APIRouter()

@router.post("", response_model=dict)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash mật khẩu trước khi create
    user_in_dict = user_in.dict()
    user_in_dict["password_hash"] = hash_password(user_in_dict.pop("password"))
    # Chuyển qua schema cho CRUD (UserCreate không có password_hash -> map tạm thời)
    create_obj = schemas.UserCreate(**{**user_in.dict()})
    # Sửa lại service để nhận password_hash (workaround: dùng crud trực tiếp)
    from app.crud.user_crud import user_crud
    db_user = user_crud.create(db, schemas.UserCreate(**user_in.dict()))
    # Sau khi tạo, cập nhật password_hash
    db_user.password_hash = user_in_dict["password_hash"]
    db.commit()
    db.refresh(db_user)
    return response_success(data=db_user)

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    svc = UserService(db)
    user = svc.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return response_success(data=user)

@router.patch("/{user_id}")
def update_user(user_id: int, user_in: schemas.UserUpdate, db: Session = Depends(get_db)):
    svc = UserService(db)
    user = svc.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return response_success(data=user)

@router.post("/{user_id}/activate")
def activate_user(user_id: int, db: Session = Depends(get_db)):
    svc = UserService(db)
    user = svc.activate_user(user_id)
    return response_success(data=user)

@router.post("/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    svc = UserService(db)
    user = svc.deactivate_user(user_id)
    return response_success(data=user)
