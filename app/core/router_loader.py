# app/core/router_loader.py
import pkgutil
import importlib
from fastapi import FastAPI
from app.api import routers

def auto_include_routers(app: FastAPI):
    """
    Tự động quét và include tất cả router trong folder app/api/routers.
    
    Cơ chế hoạt động:
    - Loader thêm prefix tổng: "/api"
    - Router con (ví dụ camera) có prefix: "/cameras"
    => Kết quả đường dẫn cuối cùng: "/api/cameras"
    """
    package_path = routers.__path__ # Đường dẫn tới folder routers
    package_name = routers.__name__ # Tên package: 'app.api.routers'

    # Duyệt qua tất cả các file trong folder
    for _, module_name, _ in pkgutil.iter_modules(package_path):
        # Bỏ qua các file __init__ hoặc file hệ thống
        if module_name.startswith("__"):
            continue

        try:
            # Import module động (tương đương: from app.api.routers import xyz)
            module = importlib.import_module(f"{package_name}.{module_name}")

            # Kiểm tra xem file đó có biến 'router' không
            if hasattr(module, "router"):
                # --- LOGIC NỐI PREFIX ---
                # prefix="/api" (từ đây) + prefix="/cameras" (từ file con) = "/api/cameras"
                app.include_router(module.router, prefix="/api")
                
                # Xử lý chuỗi để in log đẹp hơn (tránh in None nếu router con không có prefix)
                sub_prefix = module.router.prefix if module.router.prefix else ""
                print(f"✅ Đã load router: {module_name:15} -> /api{sub_prefix}")
            else:
                print(f"⚠️ Bỏ qua {module_name}: Không tìm thấy biến 'router'")
                
        except Exception as e:
            print(f"❌ Lỗi khi load router {module_name}: {e}")