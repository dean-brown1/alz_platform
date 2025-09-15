from fastapi import APIRouter
router = APIRouter()
@router.get("/legacy")
def legacy(): return {"note":"Use /v0/* routes"}
