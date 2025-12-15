# app/crud/base.py
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

# Khai báo kiểu generic
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD Base class dùng cho mọi model.
    - Tái sử dụng cho User, Camera, Order
    - Hỗ trợ create, read, update, delete, list
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> List[ModelType]:
        query = select(self.model)

        # Apply filters nếu có
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    query = query.where(getattr(self.model, field) == value)

        # Sort
        if hasattr(self.model, sort_by):
            sort_col = getattr(self.model, sort_by)
            if sort_dir == "desc":
                sort_col = sort_col.desc()
            query = query.order_by(sort_col)

        return db.execute(query.offset(skip).limit(limit)).scalars().all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.dict(exclude_unset=True)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> Optional[ModelType]:
        obj = db.get(self.model, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
