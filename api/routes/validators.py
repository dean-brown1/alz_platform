from fastapi import APIRouter
router = APIRouter()
@router.get("")
def list_validators(): return {"note":"Use /v0/validators"}
