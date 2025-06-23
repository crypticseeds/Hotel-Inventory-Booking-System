from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.connection import get_db
from ..schemas import BookingCreate, Booking
from ..db.models import Booking as BookingModel
from datetime import date, datetime
import logging

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
        db_booking = BookingModel(**booking.dict())
        logger.debug(f"Created booking model: {db_booking.__dict__}")
        db.add(db_booking)
        await db.commit()
        await db.refresh(db_booking)
        logger.debug(f"Refreshed booking data: {db_booking.__dict__}")
        
        # Convert the SQLAlchemy model instance to a dict with the exact fields expected by the Pydantic model
        booking_data = {
            "booking_id": db_booking.booking_id,
            "guest_name": db_booking.guest_name,
            "hotel_id": db_booking.hotel_id,
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