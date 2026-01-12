# app/core/docs_utils.py

from pathlib import Path
from fastapi.responses import HTMLResponse

def custom_swagger_ui_html_response(
    openapi_url: str,
    title: str,
    docs_dir: Path
) -> HTMLResponse:
    """
    Hàm tạo giao diện Swagger UI với CSS nhúng trực tiếp.
    Giúp main.py gọn gàng hơn.
    """
    css_content = ""
    css_path = docs_dir / "swagger_style.css"
    
    # Logic đọc file CSS
    if css_path.exists():
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            print("✅ Đã load custom CSS cho Swagger.")
        except Exception as e:
            print(f"⚠️ Lỗi đọc file CSS: {e}")
    
    # Tạo HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <title>{title}</title>
    <style>
        /* CSS TÙY CHỈNH */
        {css_content}
    </style>
    </head>
    <body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
        dom_id: '#swagger-ui',
        layout: "BaseLayout",
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        presets: [
            SwaggerUIBundle.presets.apis,
            SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
    }})
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)