# Thao tác DB order
# app/crud/order_crud.py
from sqlalchemy.orm import Session
from sqlalchemy import select, and_,func
from datetime import datetime, timedelta
from app.db import models, schemas
from app.crud.base import CRUDBase


class CRUDOrder(CRUDBase[models.Order, schemas.OrderCreate, schemas.OrderUpdate]):
    """
    CRUD cho Order, kế thừa từ CRUDBase.
    Thêm filter nâng cao: code, status, date presets, date range.
    """

    def filter_orders(
        self,
        db: Session,
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
        query = select(self.model)

        # Filter code
        if code:
            query = query.where(self.model.code.contains(code))

        # Filter status
        if status:
            query = query.where(self.model.status == status)

        # Date presets
        now = datetime.now()
        if date_preset == "today":
            start = datetime(now.year, now.month, now.day)
            end = start + timedelta(days=1)
            query = query.where(
                and_(self.model.created_at >= start, self.model.created_at < end))
        elif date_preset == "yesterday":
            start = datetime(now.year, now.month, now.day) - timedelta(days=1)
            end = start + timedelta(days=1)
            query = query.where(
                and_(self.model.created_at >= start, self.model.created_at < end))
        elif date_preset == "last7days":
            start = now - timedelta(days=7)
            query = query.where(self.model.created_at >= start)
        elif date_preset == "last15days":
            start = now - timedelta(days=15)
            query = query.where(self.model.created_at >= start)

        # Date range filter
        if start_date and end_date:
            query = query.where(
                and_(
                    self.model.created_at >= start_date,
                    (self.model.closed_at <= end_date) | (
                        self.model.closed_at.is_(None)),
                )
            )

        # Sort
        if hasattr(self.model, sort_by):
            sort_col = getattr(self.model, sort_by)
            if sort_dir == "desc":
                sort_col = sort_col.desc()
            query = query.order_by(sort_col)

        # Pagination
        result = db.execute(query.offset(skip).limit(limit)).scalars().all()
        total = db.execute(
            select(func.count()).select_from(self.model)).scalar()
        return result, total


order_crud = CRUDOrder(models.Order)
