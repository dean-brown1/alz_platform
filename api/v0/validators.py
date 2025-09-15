from fastapi import APIRouter
from validators.registry import load_all_validators
from validators.policy import load_policy
router = APIRouter()
@router.get("/validators")
def list_validators():
    vals = load_all_validators(); policy = load_policy()
    return {"validators":[{"code": v.code, "description": getattr(v, "description", "")} for v in vals],
            "policy":{"order": policy.order, "concurrency": policy.concurrency, "severity_overrides": policy.severity_overrides}}
