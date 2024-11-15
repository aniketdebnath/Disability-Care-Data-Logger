
from fastapi import APIRouter
from models.signal_model import run_tuning_cycle

router = APIRouter(
    prefix="/tuning",
    tags=["Tuning"],
    responses={404: {"description": "Not found"}},
)

@router.get("/start")
async def start_tuning():
    """
    Start the tuning process.
    """
    run_tuning_cycle()
    return {"message": "Tuning process started."}
