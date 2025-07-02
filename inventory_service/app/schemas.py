from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    hotel_id: int
    hotel_name: str = Field(..., max_length=100)
    location: str = Field(..., max_length=100)
    room_type: str = Field(..., max_length=50)
    date: date
    available_rooms: int = Field(..., ge=0)
    room_price: Decimal = Field(..., max_digits=8, decimal_places=2)
    demand_level: str | None = Field(None, max_length=20)


class InventoryCreate(InventoryBase):
    pass


class Inventory(InventoryBase):
    class Config:
        from_attributes = True


class InventoryPublic(BaseModel):
    hotel_name: str = Field(..., max_length=100)
    location: str = Field(..., max_length=100)
    room_type: str = Field(..., max_length=50)
    date: date
    available_rooms: int = Field(..., ge=0)
    room_price: Decimal = Field(..., max_digits=8, decimal_places=2)
    demand_level: str | None = Field(None, max_length=20)

    class Config:
        from_attributes = True 