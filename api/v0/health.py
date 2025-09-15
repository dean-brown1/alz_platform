from __future__ import annotations

import os
from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/live")
async def live():
    return {"status": "ok"}

@router.get("/ready")
async def ready():
    """
    Lightweight readiness probe. Extend with deeper checks as needed.
    """
    checks = {
        "openai_compat_base": bool(os.getenv("OPENAI_COMPAT_BASE_URL")),
        "api_key_present": bool(os.getenv("OPENAI_COMPAT_API_KEY")),
    }
    return {"status": "ok", "checks": checks}
