# app/core/router_loader.py
import pkgutil
import importlib
from fastapi import FastAPI
from app.api import routers

def auto_include_routers(app: FastAPI):
    """
    Tự động quét và include tất cả router trong folder app/api/routers.
    
    Cơ chế hoạt động:
    - Router con (ví dụ users) có prefix: "/users"
    => Kết quả đường dẫn cuối cùng: "/users"
    """
    package_path = routers.__path__ 
    package_name = routers.__name__ 

    for _, module_name, _ in pkgutil.iter_modules(package_path):
        if module_name.startswith("__"):
            continue

        try:
            module = importlib.import_module(f"{package_name}.{module_name}")

            if hasattr(module, "router"):
                # Bỏ prefix="/api", để router con tự quyết định đường dẫn của nó
                app.include_router(module.router)
                
                # Cập nhật log: chỉ in prefix của chính router đó
                actual_prefix = module.router.prefix if module.router.prefix else "/"
                print(f"✅ Đã load router: {module_name:15} -> {actual_prefix}")
            else:
                print(f"⚠️ Bỏ qua {module_name}: Không tìm thấy biến 'router'")
                
        except Exception as e:
            print(f"❌ Lỗi khi load router {module_name}: {e}")