from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List, Optional
from datetime import date
from ..db.connection import get_db
from ..service import get_inventory_by_hotel
from ..schemas import Inventory, InventoryPublic
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)

@router.get("/", response_model=List[dict])
async def read_inventory():
    return [{"item": "deluxe room", "quantity": 10}, {"item": "suite", "quantity": 5}]

@router.get("/{hotel_id}", response_model=List[InventoryPublic])
async def get_hotel_inventory(
    hotel_id: int,
    start_date: Optional[date] = Query(None, description="Start date for inventory (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date for inventory (inclusive)"),
    db: AsyncSession = Depends(get_db),
):
    inventory_list = await get_inventory_by_hotel(db, hotel_id, start_date, end_date)
    if not inventory_list:
        raise HTTPException(status_code=404, detail="Hotel not found or no inventory available")
    response = []
    for inv in inventory_list:
        response.append({
            "hotel_name": inv.hotel.hotel_name if inv.hotel else None,
            "location": inv.hotel.location if inv.hotel else None,
            "room_type": inv.room_type,
            "date": inv.date,
            "available_rooms": inv.available_rooms,
            "room_price": inv.room_price,
            "demand_level": inv.demand_level,
        })
    return response 