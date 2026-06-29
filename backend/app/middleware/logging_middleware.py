"""
Logging middleware
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger
import time, uuid


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()
        logger.info(f"[{request_id}] {request.method} {request.url.path}")
        response = await call_next(request)
        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(f"[{request_id}] {response.status_code} — {elapsed}ms")
        response.headers["X-Request-ID"] = request_id
        return response
