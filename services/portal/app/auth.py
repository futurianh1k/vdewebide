from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """
    MVP용 관리자 인증:
    - 요청 헤더 `X-Admin-Key`가 settings.admin_api_key와 일치해야 함
    - 운영에서는 SSO/리버스프록시 인증으로 대체 권장
    """

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Public assets
        if path == "/" or path.startswith("/admin") or path.startswith("/static/") or path == "/healthz":
            return await call_next(request)

        if path.startswith("/api/"):
            key = request.headers.get("x-admin-key")
            if not key or key != settings.admin_api_key:
                return JSONResponse({"error": {"code": "AUTH_FORBIDDEN"}}, status_code=403)

        return await call_next(request)

