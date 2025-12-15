from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import get_db
from app.db import schemas
from app.services.order_service import OrderService
from app.utils.pagination import paginate
from app.utils.response import response_success
from app.utils.time_utils import today, yesterday, last7days, last15days

router = APIRouter(prefix="/orders", tags=["orders"])

# Đã xóa operation_id="create_order_api"
@router.post("") 
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    svc = OrderService(db)
    order = svc.create_order(order_in)
    return response_success(data=order)

# Đã xóa operation_id="get_order_api"
@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    svc = OrderService(db)
    order = svc.get_order(order_id)
    return response_success(data=order)

# Đã xóa operation_id="update_order_api"
@router.patch("/{order_id}")
def update_order(order_id: int, order_in: schemas.OrderUpdate, db: Session = Depends(get_db)):
    svc = OrderService(db)
    order = svc.update_order(order_id, order_in)
    return response_success(data=order)

# Đã xóa operation_id="list_orders_api"
@router.get("")
def list_orders(
    page: int = Query(0, ge=0),
    page_size: int = Query(100, gt=0, le=500),
    code: str | None = None,
    status: str | None = None,
    date_preset: str | None = Query(None, pattern="^(today|yesterday|last7days|last15days)$"),
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sort_by: str = "created_at",
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    svc = OrderService(db)
    skip, limit = paginate(page, page_size)

    # Nếu preset có giá trị mà không truyền start/end -> áp preset
    if date_preset and not (start_date and end_date):
        if date_preset == "today":
            start_date, end_date = today()
        elif date_preset == "yesterday":
            start_date, end_date = yesterday()
        elif date_preset == "last7days":
            start_date, end_date = last7days()
        elif date_preset == "last15days":
            start_date, end_date = last15days()

    result = svc.filter_orders(
        skip=skip,
        limit=limit,
        code=code,
        status=status,
        date_preset=None,  # đã convert sang start/end ở trên
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return response_success(
        data=result["data"],
        total=result["total"],
        page=page,
        pageSize=page_size,
    )