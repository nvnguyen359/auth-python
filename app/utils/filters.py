# Bộ lọc chung 
# app/utils/filters.py
from typing import Dict, Any
from sqlalchemy.sql import Select

def apply_filters(query: Select, model, filters: Dict[str, Any]) -> Select:
    """
    Áp dụng bộ lọc dạng {field: value} lên query.
    Chỉ nhận các field có trong model và value khác None.
    """
    if not filters:
        return query
    for field, value in filters.items():
        if value is None:
            continue
        if hasattr(model, field):
            query = query.where(getattr(model, field) == value)
    return query
