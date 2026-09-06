import time
import uuid
from collections.abc import Awaitable, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.observability.metrics import HTTP_REQUEST_DURATION, HTTP_REQUESTS

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        started = time.perf_counter()
        try:
            response = await call_next(request)
            return response
        finally:
            elapsed = time.perf_counter() - started
            status_code = getattr(locals().get("response"), "status_code", 500)
            HTTP_REQUESTS.labels(request.method, request.url.path, status_code).inc()
            HTTP_REQUEST_DURATION.labels(request.method, request.url.path).observe(elapsed)
            if "response" in locals():
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Content-Type-Options"] = "nosniff"
                response.headers["X-Frame-Options"] = "DENY"
                response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
