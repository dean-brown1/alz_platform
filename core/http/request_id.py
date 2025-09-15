from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from uuid import uuid4
import time

HEADER = "X-Request-ID"

def new_request_id() -> str:
    return str(uuid4())

class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        rid = request.headers.get(HEADER) or new_request_id()
        request.state.request_id = rid
        t0 = time.perf_counter()
        response = await call_next(request)
        response.headers[HEADER] = rid
        response.headers["X-Elapsed-ms"] = str(int((time.perf_counter() - t0) * 1000))
        return response
