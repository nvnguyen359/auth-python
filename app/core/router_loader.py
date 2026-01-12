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
    package_path = routers.__path__ # Đường dẫn tới folder routers
    package_name = routers.__name__ # Tên package: 'app.api.routers'

    # Duyệt qua tất cả các file trong folder
    for _, module_name, _ in pkgutil.iter_modules(package_path):
        # Bỏ qua các file __init__ hoặc file không cần thiết
        if module_name.startswith("__"):
            continue

        try:
            # Import module động
            module = importlib.import_module(f"{package_name}.{module_name}")

            # Kiểm tra xem file đó có biến 'router' không
            if hasattr(module, "router"):
                # THÊM PREFIX "/api" Ở ĐÂY
                # Giúp tách biệt API với Frontend (ví dụ: /api/users thay vì /users)
                app.include_router(module.router, prefix="/api")
                
                print(f"✅ Đã load router: {module_name} -> /api{module.router.prefix}")
            else:
                print(f"⚠️ Bỏ qua {module_name}: Không tìm thấy biến 'router'")
                
        except Exception as e:
            print(f"❌ Lỗi khi load router {module_name}: {e}")