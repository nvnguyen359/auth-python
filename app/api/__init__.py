
"""
API Package
-----------
Chứa các routers cho FastAPI:
- auth_router: đăng nhập, JWT
- user_router: CRUD user
- camera_router: CRUD camera
- order_router: CRUD order
"""

from fastapi import APIRouter
from app.api.routers import auth_router, user_router, camera_router, order_router

api_router = APIRouter()
api_router.include_router(auth_router.router, prefix="/auth", tags=["Auth"])
api_router.include_router(user_router.router, prefix="/users", tags=["Users"])
api_router.include_router(camera_router.router, prefix="/cameras", tags=["Cameras"])
api_router.include_router(order_router.router, prefix="/orders", tags=["Orders"])
