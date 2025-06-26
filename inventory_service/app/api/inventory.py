from fastapi import APIRouter, Depends, Query, HTTPException, Body
from typing import List, Optional
from datetime import date
from ..db.connection import get_db
from ..service import get_inventory_by_hotel, adjust_inventory, get_hotel_name_by_id
from ..schemas import Inventory, InventoryPublic
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)

# Utility to mask PII in dicts (update PII_FIELDS if new PII fields are added in the future)
PII_FIELDS = []  # e.g., add 'guest_name' if needed in the future
def mask_pii(data):
    if isinstance(data, dict):
        return {k: ('[REDACTED]' if k in PII_FIELDS else v) for k, v in data.items()}
    return data

@router.get("/", response_model=List[dict])
async def read_inventory():
    logger.info("Fetching all inventory items")
    return [{"item": "deluxe room", "quantity": 10}, {"item": "suite", "quantity": 5}]

@router.get("/{hotel_id}", response_model=List[InventoryPublic])
async def get_hotel_inventory(
    hotel_id: int,
    start_date: Optional[date] = Query(None, description="Start date for inventory (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date for inventory (inclusive)"),
    db: AsyncSession = Depends(get_db),
):
    logger.debug(f"Fetching inventory for hotel_id={hotel_id}, start_date={start_date}, end_date={end_date}")
    inventory_list = await get_inventory_by_hotel(db, hotel_id, start_date, end_date)
    if not inventory_list:
        logger.warning(f"No inventory found for hotel_id={hotel_id}")
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
    logger.info(f"Returning {len(response)} inventory items for hotel_id={hotel_id}")
    return response

@router.get("/hotel_name/{hotel_id}")
async def get_hotel_name(hotel_id: int, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Fetching hotel name for hotel_id={hotel_id}")
    hotel_name = await get_hotel_name_by_id(db, hotel_id)
    if hotel_name is None:
        logger.error(f"Hotel not found for hotel_id={hotel_id}")
        raise HTTPException(status_code=404, detail="Hotel not found")
    return {"hotel_id": hotel_id, "hotel_name": hotel_name}

class InventoryAdjustRequest(BaseModel):
    room_type: str
    date: date
    num_rooms: int = 1

@router.post("/{hotel_id}/adjust")
async def adjust_inventory_endpoint(
    hotel_id: int,
    payload: InventoryAdjustRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info(f"Adjusting inventory for hotel_id={hotel_id}, payload={mask_pii(payload.dict())}")
    success = await adjust_inventory(
        db,
        hotel_id=hotel_id,
        room_type=payload.room_type,
        date=payload.date,
        num_rooms=payload.num_rooms,
    )
    if not success:
        logger.warning(f"Failed to adjust inventory for hotel_id={hotel_id}, payload={mask_pii(payload.dict())}")
        raise HTTPException(status_code=400, detail="Not enough available rooms or invalid request.")
    logger.info(f"Inventory adjusted for hotel_id={hotel_id}, payload={mask_pii(payload.dict())}")
    return {"success": True, "message": "Inventory adjusted."} 