from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.db import schemas
from app.db.session import get_db
from app.crud.user_crud import user_crud
from app.utils.response import response_success

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=dict)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Kiểm tra tồn tại
    existing_user = user_crud.get_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Username already registered"
        )

    # 2. Tạo user (Logic hash password nằm trong CRUD)
    db_user = user_crud.create(db, obj_in=user_in)
    
    # 3. Chuyển đổi sang JSON-compatible dict (Sẽ xử lý luôn cả datetime)
    data_response = jsonable_encoder(db_user)
    
    # Bảo mật: Xóa hash password
    data_response.pop("password_hash", None)
    
    # Đảm bảo trả về múi giờ Việt Nam trong response
    return response_success(data=data_response)

@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return response_success(data=user)

@router.post("/{user_id}/activate")
def activate_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.activate(db, user_id=user_id)
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    return response_success(data=user)

@router.post("/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    user = user_crud.deactivate(db, user_id=user_id)
    if not user:
         raise HTTPException(status_code=404, detail="User not found")
    return response_success(data=user)