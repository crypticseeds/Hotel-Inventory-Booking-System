from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from uuid import UUID
from typing import Optional


class BookingBase(BaseModel):
    hotel_id: int
    arrival_date: date
    stay_length: int = Field(..., gt=0)
    room_type: str = Field(..., max_length=50)
    adults: int = Field(..., gt=0)
    children: int = Field(..., ge=0)
    meal_plan: Optional[str] = Field(None, max_length=50)
    market_segment: Optional[str] = Field(None, max_length=50)
    is_weekend: bool
    is_holiday: bool
    booking_channel: Optional[str] = Field(None, max_length=50)
    room_price: Decimal = Field(..., max_digits=8, decimal_places=2, gt=0)
    reservation_status: str = Field(..., max_length=20)


class BookingCreate(BookingBase):
    pass


class Booking(BookingBase):
    booking_id: UUID
    check_out_date: date
    created_at: date

    class Config:
        orm_mode = True 