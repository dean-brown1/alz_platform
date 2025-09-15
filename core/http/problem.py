from __future__ import annotations
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

class Problem(BaseModel):
    type: str = "about:blank"
    title: str
    detail: str | None = None
    status: int
    instance: str | None = None

def problem_response(status: int, title: str, detail: str | None = None, type_: str | None = None):
    body = Problem(status=status, title=title, detail=detail, type=type_ or "about:blank").model_dump()
    return JSONResponse(status_code=status, content=body)

async def problem_http_exception_handler(request: Request, exc):
    title = getattr(exc, "detail", "HTTP Error")
    return problem_response(status=exc.status_code, title=str(title), detail=None)

async def problem_validation_exception_handler(request: Request, exc):
    return problem_response(status=422, title="Unprocessable Entity", detail=str(exc))
