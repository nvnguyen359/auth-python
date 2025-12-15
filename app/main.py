# AD-OCV1/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.middleware.cors import CORSMiddleware
from app.api.routers import auth_router, user_router, camera_router, order_router
from app.core.auth_middleware import AuthMiddleware
from app.core.config import settings
import threading
from app.db.session import get_db # Hàm trả về generator cho DB Session
from app.services.camera_management_service import run_camera_upsert_loop
from scripts.check_db import main as check_db_main
# Khởi tạo ứng dụng FastAPI với các thông tin chung (metadata)
app = FastAPI(
    title="AD-OCV1 API Documentation",
    version="1.0.0",
    description="API Documentation for the AD-OCV1 project - User, Camera, and Order Management System.",
    openapi_tags=[
        {"name": "auth", "description": "Authentication and Token Generation (Login, Get User Info)."},
        {"name": "users", "description": "User CRUD and Account Management (Requires Admin/Supervisor)."},
        {"name": "cameras", "description": "Camera Device CRUD and Connection Status."},
        {"name": "orders", "description": "Order/Session Management and Tracking."},
    ]
)

# Thêm Middleware CORS
app.add_middleware(
    CORSMiddleware,
    # SỬA LỖI TẠI ĐÂY: Thay CORS_ORIGINS.split(",") bằng settings.allowed_origins
    allow_origins=settings.allowed_origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Thêm Middleware xác thực tùy chỉnh
app.add_middleware(AuthMiddleware)

# Mount Static files (CSS cho Swagger UI)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "docs"),
    name="static",
)

# Thêm các Router
# Lưu ý: Nếu auth_router có prefix, cần thêm vào đây. Hiện tại không có prefix.
app.include_router(auth_router.router, tags=["auth"]) 
app.include_router(user_router.router, prefix="/users", tags=["users"])
app.include_router(camera_router.router, prefix="/cameras", tags=["cameras"])
app.include_router(order_router.router, prefix="/orders", tags=["orders"])


# Định nghĩa cơ chế OpenAPI tùy chỉnh để thêm Security Scheme
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    # Lấy lược đồ tự động sinh
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags
    )
# SỬA LỖI: Thay đổi Security Scheme sang OAuth2 Password Flow
    # Điều này sẽ hiển thị form Username/Password khi bấm "Authorize"
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/login",  # Đường dẫn API login để Swagger gửi user/pass tới
                    "scopes": {}
                }
            }
        }
    }
    
    # Áp dụng yêu cầu xác thực cho tất cả các Path
    for path, path_item in openapi_schema["paths"].items():
        for method_info in path_item.values():
            tags = method_info.get("tags", [])
            
            # Áp dụng security cho các endpoint KHÔNG thuộc tag 'auth'
            if tags and "auth" not in tags:
                method_info["security"] = [{"OAuth2PasswordBearer": []}]
            
            # Xử lý riêng cho endpoint "/me" (nằm trong tag "auth" nhưng cần xác thực)
            if tags and "auth" in tags and path.endswith("/me"):
                method_info["security"] = [{"OAuth2PasswordBearer": []}]
                
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.on_event("startup")
async def startup_event():
    check_db_main()# Gọi hàm main() từ scripts/check_db.py tạo db
    # Chạy vòng lặp upsert camera mỗi 5 giây trong luồng riêng
    camera_thread = threading.Thread(
        target=run_camera_upsert_loop, 
        args=(get_db, 5), # Truyền hàm get_db (factory) và khoảng thời gian
        daemon=True
    )
    camera_thread.start()

# Tùy chỉnh Swagger UI HTML để load CSS
@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    # Đường dẫn đến file CSS tùy chỉnh của bạn
    swagger_css_url = request.url_for("static", path="swagger_style.css")

    # Hàm lấy HTML mặc định của Swagger UI (tự động)
    from fastapi.openapi.docs import get_swagger_ui_html
    html_content = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_css_url=swagger_css_url
    )
    return html_content

# Endpoint gốc
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to AD-OCV1 API. See documentation at /docs"}