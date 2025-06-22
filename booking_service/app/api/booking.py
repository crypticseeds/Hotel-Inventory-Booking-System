from fastapi import APIRouter

router = APIRouter(
    prefix="/booking",
    tags=["booking"],
)

@router.get("/")
async def read_bookings():
    return [{"booking_id": "booking123", "item": "deluxe room"}, {"booking_id": "booking456", "item": "suite"}]

@router.post("/")
async def create_booking(item: str):
    return {"status": "created", "booking_id": "booking789", "item": item} 