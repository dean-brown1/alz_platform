from fastapi import APIRouter
router = APIRouter()
@router.get("/board/ping")
def ping(): return {"ok": True}
