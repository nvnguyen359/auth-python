# AD-OCV1/app/main.py

import os
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.middleware.cors import CORSMiddleware

# --- Import nội bộ ---
from app.core.config import settings
from app.core.auth_middleware import AuthMiddleware
from app.core.router_loader import auto_include_routers
from app.core.openapi_config import configure_openapi
from app.db.session import get_db
from app.services.camera_management_service import run_camera_upsert_loop
from scripts.check_db import main as check_db_main
import threading

# 1. Định nghĩa đường dẫn tới thư mục client
# Đi lên 2 cấp từ app/main.py để về root, sau đó vào client/browser
BASE_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIR = BASE_DIR / "client" / "browser"

# 2. Khởi tạo App
app = FastAPI(
    title="AD-OCV1 API Documentation",
    version="1.0.0",
    description="API Documentation for the AD-OCV1 project.",
    docs_url=None, # Tắt docs mặc định để tự cấu hình bên dưới
    redoc_url=None
)

# 3. Cấu hình Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

# 4. Load Routers & Config
auto_include_routers(app)
configure_openapi(app)

# 5. Startup Events
@app.on_event("startup")
async def startup_event():
    check_db_main()
    camera_thread = threading.Thread(
        target=run_camera_upsert_loop, 
        args=(get_db, 5),
        daemon=True
    )
    camera_thread.start()

# 6. Custom Swagger UI
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "docs"), name="static_docs")

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_css_url=request.url_for("static_docs", path="swagger_style.css")
    )

# ==========================================
# CẤU HÌNH SERVE FRONTEND (CLIENT/BROWSER)
# ==========================================

# Kiểm tra thư mục client có tồn tại không để tránh lỗi crash
if CLIENT_DIR.exists():
    # Cách 1: Nếu client build ra folder 'assets' hoặc 'static' riêng (React/Vue thường làm thế này)
    if (CLIENT_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=CLIENT_DIR / "assets"), name="assets")

    # Cách 2: Route đặc biệt để phục vụ các file tĩnh nằm ngay ngoài cùng (như favicon.ico, robots.txt)
    @app.get("/{file_path:path}", include_in_schema=False)
    async def serve_static_files(file_path: str):
        file_location = CLIENT_DIR / file_path
        # Nếu là file tồn tại -> trả về file
        if file_location.is_file():
            return FileResponse(file_location)
        # Nếu không tìm thấy file và không phải API -> trả về index.html (cho SPA routing)
        # Lưu ý: Các API routers đã được check trước ở trên, nên không sợ bị đè.
        return FileResponse(CLIENT_DIR / "index.html")

    # Route gốc: Trả về index.html
    @app.get("/", include_in_schema=False)
    async def root():
        return FileResponse(CLIENT_DIR / "index.html")
else:
    # Fallback nếu chưa có thư mục client
    @app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Client directory not found. Please build frontend to 'client/browser'"}

# ==========================================
# CHẠY APP VỚI CONFIG TỪ .ENV
# ==========================================
if __name__ == "__main__":
    print(f"🚀 Starting server at http://{settings.HOST}:{settings.PORT}")
    print(f"📂 Serving client from: {CLIENT_DIR}")
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )