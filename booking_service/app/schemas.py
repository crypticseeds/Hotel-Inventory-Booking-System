from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional, Any


class BookingBase(BaseModel):
    guest_name: str = Field(..., max_length=100)
    hotel_name: Optional[str] = Field(None, max_length=100)
    arrival_date: date
    stay_length: int = Field(..., gt=0)
    room_type: str = Field(..., max_length=50)
    adults: int = Field(..., gt=0)
    children: int = Field(..., ge=0)
    meal_plan: Optional[str] = Field(None, max_length=50)
    market_segment: Optional[str] = Field(None, max_length=50)
    is_holiday: bool
    booking_channel: Optional[str] = Field(None, max_length=50)
    room_price: Decimal = Field(..., max_digits=8, decimal_places=2, gt=0)


class BookingCreate(BookingBase):
    hotel_id: int
    hotel_name: Optional[str] = None  # Not required for creation


class Booking(BookingBase):
    booking_id: str
    check_out_date: date
    created_at: date
    reservation_status: str = Field(..., max_length=20)

    class Config:
        from_attributes = True


class BookingUpdate(BaseModel):
    guest_name: Optional[str] = Field(None, max_length=100)
    arrival_date: Optional[date] = None
    stay_length: Optional[int] = Field(None, gt=0)
    room_type: Optional[str] = Field(None, max_length=50)
    adults: Optional[int] = Field(None, gt=0)
    children: Optional[int] = Field(None, ge=0)
    # You can add more fields here if you want to allow them to be patched

    class Config:
        extra = "forbid"  # Forbid fields not explicitly listed 