from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db import schemas
from app.db.session import get_db
from app.crud.order_crud import order_crud
from app.utils.response import response_success

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("")
def get_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    code: Optional[str] = Query(
        None, description="Tìm kiếm theo mã (hỗ trợ nhiều mã cách nhau bằng dấu phẩy)"
    ),
    status: Optional[str] = Query(
        None, description="Lọc theo trạng thái: packing, closed, error..."
    ),
    date_preset: Optional[str] = Query(
        None, description="Lọc nhanh: today, yesterday, last7days, last15days"
    ),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    """
    Lấy danh sách đơn hàng với bộ lọc nâng cao và múi giờ VN.
    """
    orders, total = order_crud.filter_orders(
        db=db,
        skip=skip,
        limit=limit,
        code=code,
        status=status,
        date_preset=date_preset,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )

    return response_success(
        data={
            "items": jsonable_encoder(orders),
            "total": total,
            "page": (skip // limit) + 1,
            "limit": limit,
        }
    )


@router.post("", response_model=dict)
def create_order(obj_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    Tạo đơn hàng mới với giờ Việt Nam tự động.
    """
    # Sử dụng hàm create_with_vn_time đã viết trong CRUD
    new_order = order_crud.create_with_vn_time(db, obj_in=obj_in)
    return response_success(data=jsonable_encoder(new_order))


@router.post("/{order_id}/start")
def start_processing_order(order_id: int, db: Session = Depends(get_db)):
    """
    Cập nhật trạng thái bắt đầu xử lý đơn hàng (Gán start_at = giờ VN).
    """
    order = order_crud.start_order(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return response_success(data=jsonable_encoder(order))


@router.post("/{order_id}/close")
def close_order(order_id: int, status: str = "closed", db: Session = Depends(get_db)):
    """
    Kết thúc đơn hàng (Gán closed_at = giờ VN).
    """
    order = order_crud.close_order(db, order_id=order_id, status=status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return response_success(data=jsonable_encoder(order))


@router.get("/{order_id}")
def get_order_detail(order_id: int, db: Session = Depends(get_db)):
    """
    Lấy chi tiết một đơn hàng.
    """
    order = order_crud.get(db, id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return response_success(data=jsonable_encoder(order))


@router.get("")
def list_orders(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    code: str = Query(None),
    status: str = Query(None),
    date_preset: str = Query(None),
    sort_by: str = "created_at",
    sort_dir: str = "desc",
):
    # Trả về Flat List (Cha và Con nằm chung danh sách)
    items, total = order_crud.filter_orders(
        db,
        skip=skip,
        limit=limit,
        code=code,
        status=status,
        date_preset=date_preset,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return response_success(data={"items": jsonable_encoder(items), "total": total})


@router.delete("/all")
def clear_all_data(db: Session = Depends(get_db)):
    """Xóa sạch đơn hàng và file vật lý"""
    count = order_crud.remove_all(db)
    return response_success(
        message=f"Đã xóa {count} đơn hàng và dọn dẹp file thành công."
    )
