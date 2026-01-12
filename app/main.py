# app/main.py

import uvicorn
import threading
from pathlib import Path
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

# --- Import nội bộ ---
from app.core.config import settings
from app.core.auth_middleware import AuthMiddleware
from app.core.router_loader import auto_include_routers
from app.core.openapi_config import configure_openapi
from app.core.docs_utils import custom_swagger_ui_html_response # <--- Import hàm vừa tách
from app.db.session import get_db
from app.services.camera_management_service import run_camera_upsert_loop
from scripts.check_db import main as check_db_main

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN
# ==========================================
APP_DIR = Path(__file__).resolve().parent
DOCS_DIR = APP_DIR / "docs"
CLIENT_DIR = APP_DIR.parent / "client" / "browser"

# 2. Khởi tạo App
app = FastAPI(
    title="AD-OCV1 API Documentation",
    version="1.0.0",
    docs_url=None, # Tắt URL mặc định
    redoc_url=None
)

# 3. Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AuthMiddleware)

# 4. Load Config
auto_include_routers(app) 
configure_openapi(app)

# 5. Startup
@app.on_event("startup")
async def startup_event():
    print(f"🚀 Server running at http://{settings.HOST}:{settings.PORT}")
    try:
        check_db_main()
    except Exception as e:
        print(f"⚠️ Warning: Check DB failed: {e}")

    camera_thread = threading.Thread(
        target=run_camera_upsert_loop, 
        args=(get_db, 5),
        daemon=True
    )
    camera_thread.start()

# ==========================================
# 6. SWAGGER UI (Đã dùng hàm tách biệt)
# ==========================================
@app.get("/docs", include_in_schema=False)
async def docs_page():
    # Gọi hàm từ file docs_utils.py để lấy HTML
    return custom_swagger_ui_html_response(
        openapi_url=app.openapi_url,
        title=app.title,
        docs_dir=DOCS_DIR
    )

# ==========================================
# 7. SERVE FRONTEND & CATCH-ALL
# ==========================================
if CLIENT_DIR.exists():
    if (CLIENT_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(CLIENT_DIR / "assets")), name="assets")

    @app.get("/{file_path:path}", include_in_schema=False)
    async def serve_spa(file_path: str):
        if file_path.startswith("api/") or file_path == "openapi.json":
             return JSONResponse({"detail": "Not Found"}, status_code=404)

        file_location = CLIENT_DIR / file_path
        if file_location.is_file():
            return FileResponse(file_location)
        
        return FileResponse(CLIENT_DIR / "index.html")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)