from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.connection import get_db
from ..schemas import BookingCreate, Booking
from ..db.models import Booking as BookingModel
from datetime import date, datetime, timedelta
import logging
import httpx

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

@router.get("/")
async def read_bookings(db: AsyncSession = Depends(get_db)):
    return [{"booking_id": "example"}]

@router.post("/", response_model=Booking)
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db)):
    try:
        logger.debug(f"Received booking data: {booking.dict()}")
        booking_dict = booking.dict()
        if 'hotel_name' in booking_dict:
            booking_dict.pop('hotel_name')
        db_booking = BookingModel(**booking_dict)
        logger.debug(f"Created booking model: {db_booking.__dict__}")
        db.add(db_booking)
        await db.commit()
        await db.refresh(db_booking)
        logger.debug(f"Refreshed booking data: {db_booking.__dict__}")
        
        # Adjust inventory for each night of the stay
        inventory_service_url = "http://localhost:8001/inventory"
        for day in range(booking.stay_length):
            adjust_date = booking.arrival_date + timedelta(days=day)
            adjust_payload = {
                "room_type": booking.room_type,
                "date": str(adjust_date),
                "num_rooms": 1
            }
            async with httpx.AsyncClient() as client:
                adjust_url = f"{inventory_service_url}/{booking.hotel_id}/adjust"
                try:
                    resp = await client.post(adjust_url, json=adjust_payload, timeout=5.0)
                    if resp.status_code != 200:
                        logger.warning(f"Inventory adjustment failed for {adjust_payload}: {resp.text}")
                except Exception as e:
                    logger.warning(f"Error calling inventory service: {e}")
        
        # Fetch hotel_name from inventory service
        async with httpx.AsyncClient() as client:
            hotel_name_url = f"{inventory_service_url}/hotel_name/{db_booking.hotel_id}"
            hotel_resp = await client.get(hotel_name_url, timeout=5.0)
            if hotel_resp.status_code == 200:
                hotel_name = hotel_resp.json().get("hotel_name")
            else:
                hotel_name = None
        
        # Convert the SQLAlchemy model instance to a dict with the exact fields expected by the Pydantic model
        booking_data = {
            "booking_id": db_booking.booking_id,
            "guest_name": db_booking.guest_name,
            "hotel_name": hotel_name,
            "arrival_date": db_booking.arrival_date,
            "stay_length": db_booking.stay_length,
            "check_out_date": db_booking.check_out_date,
            "room_type": db_booking.room_type,
            "adults": db_booking.adults,
            "children": db_booking.children,
            "meal_plan": db_booking.meal_plan,
            "market_segment": db_booking.market_segment,
            "is_weekend": db_booking.is_weekend,
            "is_holiday": db_booking.is_holiday,
            "booking_channel": db_booking.booking_channel,
            "room_price": db_booking.room_price,
            "reservation_status": db_booking.reservation_status,
            "created_at": db_booking.created_at.date() if hasattr(db_booking.created_at, 'date') else db_booking.created_at
        }
        logger.debug(f"Final response data: {booking_data}")
        return booking_data
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) 