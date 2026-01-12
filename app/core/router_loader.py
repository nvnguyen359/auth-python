# app/core/router_loader.py
import pkgutil
import importlib
from fastapi import FastAPI
from app.api import routers

def auto_include_routers(app: FastAPI):
    """
    Tự động quét và include tất cả router trong folder app/api/routers
    Yêu cầu: Trong mỗi file phải có biến 'router = APIRouter(...)'
    """
    package_path = routers.__path__
    package_name = routers.__name__

    for _, module_name, _ in pkgutil.iter_modules(package_path):
        if module_name.startswith("__"):
            continue

        try:
            module = importlib.import_module(f"{package_name}.{module_name}")
            if hasattr(module, "router"):
                app.include_router(module.router)
                print(f"✅ Đã load router: {module_name}")
            else:
                print(f"⚠️ Bỏ qua {module_name}: Không tìm thấy biến 'router'")
        except Exception as e:
            print(f"❌ Lỗi khi load router {module_name}: {e}")