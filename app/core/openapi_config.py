# app/core/openapi_config.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def configure_openapi(app: FastAPI):
    """
    Thiết lập custom OpenAPI schema để hỗ trợ nút Authorize (OAuth2)
    """
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=app.openapi_tags
        )

        # Thêm Security Scheme (OAuth2 Password Flow)
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/login",
                        "scopes": {}
                    }
                }
            }
        }
        
        # Áp dụng bảo mật cho các endpoint (trừ tag 'auth')
        for path, path_item in openapi_schema["paths"].items():
            for method_info in path_item.values():
                tags = method_info.get("tags", [])
                
                if tags and "auth" not in tags:
                    method_info["security"] = [{"OAuth2PasswordBearer": []}]
                
                # Ngoại lệ: endpoint /me cần bảo mật dù nằm trong auth
                if tags and "auth" in tags and path.endswith("/me"):
                    method_info["security"] = [{"OAuth2PasswordBearer": []}]
                    
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    # Gán hàm custom vào app
    app.openapi = custom_openapi