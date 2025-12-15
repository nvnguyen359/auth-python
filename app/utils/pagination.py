# app/utils/pagination.py
from typing import Tuple

def paginate(page: int, page_size: int, max_page_size: int = 500) -> Tuple[int, int]:
    """
    Chuẩn hóa tham số phân trang:
    - page: 0-based (nếu <0 thì về 0)
    - page_size: cắt ngưỡng tối đa
    Trả về (skip, limit)
    """
    if page < 0:
        page = 0
    if page_size <= 0:
        page_size = 1
    if page_size > max_page_size:
        page_size = max_page_size
    skip = page * page_size
    limit = page_size
    return skip, limit
