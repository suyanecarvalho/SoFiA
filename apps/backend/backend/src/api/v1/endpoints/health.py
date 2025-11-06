from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def read_health():
    """
    Check the health of the application.
    """
    return {"status": "ok"}
