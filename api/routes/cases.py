from fastapi import APIRouter
from core.bus.events import get_events
router = APIRouter()
@router.get("/events")
def events(): return {"events": get_events()}
