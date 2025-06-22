from fastapi import APIRouter

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

@router.get("/")
async def read_bookings():
    return [{"booking_id": "example"}]

@router.post("/")
async def create_booking(item: str):
    return {"status": "created", "booking_id": "booking789", "item": item} 