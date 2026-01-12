# app/core/openapi_config.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def configure_openapi(app: FastAPI):
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

        # SỬA QUAN TRỌNG: Thêm /api vào trước /login
        openapi_schema["components"]["securitySchemes"] = {
            "OAuth2PasswordBearer": {
                "type": "oauth2",
                "flows": {
                    "password": {
                        "tokenUrl": "/api/login",  # <--- CHÚ Ý DÒNG NÀY
                        "scopes": {}
                    }
                }
            }
        }
        
        # Áp dụng bảo mật cho các endpoint
        for path, path_item in openapi_schema["paths"].items():
            for method_info in path_item.values():
                tags = method_info.get("tags", [])
                if tags and "auth" not in tags:
                    method_info["security"] = [{"OAuth2PasswordBearer": []}]
                if tags and "auth" in tags and path.endswith("/me"):
                    method_info["security"] = [{"OAuth2PasswordBearer": []}]
                    
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi