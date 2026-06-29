"""
Rate limiting middleware using Redis
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
import time


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: dict = {}

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/", "/health", "/api/docs", "/api/redoc"]:
            return await call_next(request)

        client_ip = request.client.host
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW
        limit = settings.RATE_LIMIT_REQUESTS

        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items()
            if now - v["start"] < window
        }

        if client_ip not in self.requests:
            self.requests[client_ip] = {"count": 1, "start": now}
        else:
            self.requests[client_ip]["count"] += 1
            if self.requests[client_ip]["count"] > limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Max {limit} requests per {window} seconds",
                        "retry_after": int(window - (now - self.requests[client_ip]["start"])),
                    },
                )

        return await call_next(request)
