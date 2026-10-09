from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/")
def root():
    return {
        "message": "Food Receipt AI Agent API",
        "status": "running",
    }


@router.get("/health")
def health_check():
    return {"status": "healthy"}