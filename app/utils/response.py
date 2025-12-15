# Chuẩn hóa JSON envelope 
# app/utils/response.py
from typing import Any, Optional

def response_success(
    data: Any = None,
    mes: str = "success",
    code: int = 200,
    total: Optional[int] = None,
    page: Optional[int] = None,
    pageSize: Optional[int] = None,
) -> dict:
    """
    Chuẩn hóa response thành JSON envelope cho kết quả thành công.
    """
    resp = {
        "code": code,
        "mes": mes,
        "data": data if data is not None else [],
    }
    if total is not None:
        resp["total"] = total
    if page is not None:
        resp["page"] = page
    if pageSize is not None:
        resp["pageSize"] = pageSize
    return resp


def response_error(
    mes: str = "error",
    code: int = 400,
    data: Any = None,
) -> dict:
    """
    Chuẩn hóa response thành JSON envelope cho lỗi.
    """
    return {
        "code": code,
        "mes": mes,
        "data": data if data is not None else [],
    }
