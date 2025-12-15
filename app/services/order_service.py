# Nghiệp vụ order (filter, phân trang, sort) 
# app/services/order_service.py
from sqlalchemy.orm import Session
from datetime import datetime
from app.crud.order_crud import order_crud
from app.db import schemas

class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order_in: schemas.OrderCreate):
        return order_crud.create(self.db, order_in)

    def get_order(self, order_id: int):
        return order_crud.get(self.db, order_id)

    def update_order(self, order_id: int, order_in: schemas.OrderUpdate):
        db_order = order_crud.get(self.db, order_id)
        if not db_order:
            return None
        return order_crud.update(self.db, db_order, order_in)

    def delete_order(self, order_id: int):
        return order_crud.remove(self.db, order_id)

    def filter_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        code: str = None,
        status: str = None,
        date_preset: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ):
        result, total = order_crud.filter_orders(
            self.db,
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
        return {"data": result, "total": total, "page": skip // limit, "pageSize": limit}
