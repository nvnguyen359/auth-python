
# app/crud/__init__.py
"""
CRUD package cho AD-OCV1.
Chứa các lớp thao tác DB cho User, Camera, Order.
"""

from .user_crud import user_crud
from .camera_crud import camera_crud
from .order_crud import order_crud

__all__ = ["user_crud", "camera_crud", "order_crud"]
