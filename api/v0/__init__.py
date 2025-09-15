from __future__ import annotations
from fastapi import APIRouter

# This is the top-level v0 router that your app should include with prefix="/v0"
router = APIRouter()

# Import and mount sub-routers for v0
from . import jobs as jobs  # noqa: E402,F401

# Mount /v0/jobs and /v0/jobs/{id}
router.include_router(jobs.router, prefix="")
# If you also have other modules like board, validators, etc., include them similarly:
# from . import board as board
# router.include_router(board.router, prefix="")
