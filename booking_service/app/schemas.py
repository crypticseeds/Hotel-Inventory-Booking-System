from datetime import date
from decimal import Decimal
from typing import Optional

import httpx
from fastapi import HTTPException
from pydantic import BaseModel, Field


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
    room_price: Optional[Decimal] = Field(None, max_digits=8, decimal_places=2, gt=0)
    total_price: Optional[Decimal] = Field(None, max_digits=10, decimal_places=2, gt=0)


class BookingCreate(BaseModel):
    guest_name: str = Field(..., max_length=100)
    arrival_date: date
    stay_length: int = Field(..., gt=0)
    room_type: str = Field(..., max_length=50)
    adults: int = Field(..., gt=0)
    children: int = Field(..., ge=0)
    meal_plan: Optional[str] = Field(None, max_length=50)
    market_segment: Optional[str] = Field(None, max_length=50)
    is_holiday: bool
    booking_channel: Optional[str] = Field(None, max_length=50)
    hotel_id: int


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


# Always fetch room_price from inventory, since it's not in the request
async def fetch_room_price(booking):
    inventory_service_url = "http://localhost:8001/inventory"
    inventory_url = f"{inventory_service_url}/{booking.hotel_id}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            inventory_url,
            params={
                "start_date": str(booking.arrival_date),
                "end_date": str(booking.arrival_date),
            },
        )
        if resp.status_code == 200:
            inventory_list = resp.json()
            price_found = False
            for item in inventory_list:
                if item["room_type"] == booking.room_type and str(item["date"]) == str(
                    booking.arrival_date
                ):
                    booking_dict = booking.dict()
                    booking_dict["room_price"] = item["room_price"]
                    price_found = True
                    break
            if not price_found:
                raise HTTPException(
                    status_code=400,
                    detail="Room price not found in inventory for the given hotel, room type, and date.",
                )
        else:
            raise HTTPException(
                status_code=400, detail="Failed to fetch inventory for room price."
            )
    return booking_dict
