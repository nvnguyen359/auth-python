# app/crud/order_crud.py
import os
import pytz
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta
from app.db import models, schemas
from app.crud.base import CRUDBase

class CRUDOrder(CRUDBase[models.Order, schemas.OrderCreate, schemas.OrderUpdate]):
    """
    CRUD Order Nâng Cao:
    - Xử lý múi giờ Việt Nam (ICT).
    - Logic Family Code (Cha - Con - Chính nó).
    - Tự động dọn dẹp Video/Avatar khi xóa dữ liệu.
    """

    def _get_vn_now(self):
        """Lấy thời gian hiện tại chuẩn Asia/Ho_Chi_Minh"""
        return datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))

    def remove_all(self, db: Session) -> int:
        """
        Xóa toàn bộ dữ liệu Order và dọn dẹp file vật lý trên ổ đĩa.
        """
        all_orders = db.query(self.model).all()
        base_path = os.getcwd()

        for order in all_orders:
            # Xử lý xóa cả Video và Avatar
            for file_attr in [order.path_video, order.path_avatar]:
                if file_attr:
                    full_path = file_attr if os.path.isabs(file_attr) else os.path.join(base_path, file_attr)
                    try:
                        if os.path.exists(full_path):
                            os.remove(full_path)
                    except Exception as e:
                        print(f"[OrderCRUD] ⚠️ Không thể xóa file: {full_path} | {e}")

        # Xóa bản ghi trong database
        rows_deleted = db.query(self.model).delete()
        db.commit()
        return rows_deleted

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
        # Sử dụng joinedload để lấy luôn thông tin cha (hỗ trợ Flat List hiển thị đủ info)
        query = select(self.model).options(joinedload(self.model.parent))
        vn_now = self._get_vn_now()

        # --- 1. LOGIC FILTER CODE (Family Logic - Ưu tiên hàng đầu) ---
        if code:
            # Hỗ trợ search nhiều code cách nhau bởi dấu phẩy
            code_list = [c.strip() for c in code.split(",") if c.strip()]
            
            # Subqueries tìm gia phả: Cha của mã này, và mã này là cha của ai
            conditions = [self.model.code.contains(c) for c in code_list]
            sub_ids = select(self.model.id).where(or_(*conditions))
            sub_parent_ids = select(self.model.parent_id).where(or_(*conditions))

            query = query.where(
                or_(
                    or_(*conditions),                # Chính nó
                    self.model.parent_id.in_(sub_ids), # Các con của nó
                    self.model.id.in_(sub_parent_ids)  # Cha của nó
                )
            )
            # Khi có Code, hệ thống bỏ qua lọc ngày để lấy toàn bộ lịch sử gia phả

        else:
            # --- 2. LOGIC DATE FILTER (Chỉ chạy khi KHÔNG có code) ---
            today_start = vn_now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if date_preset == "today":
                query = query.where(and_(self.model.created_at >= today_start, 
                                         self.model.created_at < today_start + timedelta(days=1)))
            elif date_preset == "yesterday":
                start = today_start - timedelta(days=1)
                query = query.where(and_(self.model.created_at >= start, self.model.created_at < today_start))
            elif date_preset == "last7days":
                query = query.where(self.model.created_at >= today_start - timedelta(days=7))
            elif date_preset == "last15days":
                query = query.where(self.model.created_at >= today_start - timedelta(days=15))

            if start_date and end_date:
                query = query.where(
                    and_(
                        self.model.created_at >= start_date,
                        or_(self.model.closed_at <= end_date, self.model.closed_at.is_(None))
                    )
                )

        # --- 3. FILTER STATUS ---
        if status:
            query = query.where(self.model.status == status)

        # --- 4. SORTING ---
        if hasattr(self.model, sort_by):
            sort_col = getattr(self.model, sort_by)
            query = query.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())

        # --- 5. PAGINATION & TOTAL COUNT ---
        # Đếm tổng record sau khi đã áp dụng các bộ lọc (Để phân trang chính xác)
        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar() or 0
        
        # Lấy dữ liệu
        result = db.execute(query.offset(skip).limit(limit)).scalars().all()
        return result, total

    def start_order(self, db: Session, order_id: int):
        db_obj = self.get(db, id=order_id)
        if db_obj:
            db_obj.status = "processing"
            db_obj.start_at = self._get_vn_now()
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def close_order(self, db: Session, order_id: int, status: str = "closed"):
        db_obj = self.get(db, id=order_id)
        if db_obj:
            db_obj.status = status
            db_obj.closed_at = self._get_vn_now()
            db.commit()
            db.refresh(db_obj)
        return db_obj

order_crud = CRUDOrder(models.Order)