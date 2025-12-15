# Middleware xử lý xác thực, parse token 
# app/core/auth_middleware.py
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_access_token
from app.crud.user_crud import user_crud
from app.db.session import SessionLocal

class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware để parse Bearer token từ header Authorization.
    Nếu token hợp lệ -> gắn current_user vào request.state.
    """

    async def dispatch(self, request: Request, call_next):
        if "authorization" in request.headers:
            auth_header = request.headers["authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = decode_access_token(token)
                if payload and "sub" in payload:
                    db = SessionLocal()
                    user = user_crud.get_by_username(db, payload["sub"])
                    db.close()
                    if user and user.is_active == 1:
                        request.state.current_user = user
                    else:
                        return JSONResponse(
                            status_code=401,
                            content={"code": 401, "mes": "Unauthorized", "data": []},
                        )
        response = await call_next(request)
        return response
