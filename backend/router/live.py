from fastapi import APIRouter

router = APIRouter(tags=["liveness"])

@router.get("/api")
def live_check():
    return {"status": "API is live"}