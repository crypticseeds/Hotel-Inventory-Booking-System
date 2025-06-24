from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date
from ..db.models import Inventory, Hotel
from sqlalchemy.orm import selectinload
from sqlalchemy import update, desc
from sqlalchemy.exc import NoResultFound

async def get_inventory_by_hotel(
    db: AsyncSession,
    hotel_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Inventory]:
    query = (
        select(Inventory)
        .options(selectinload(Inventory.hotel))
        .where(Inventory.hotel_id == hotel_id)
    )
    if start_date:
        query = query.where(Inventory.date >= start_date)
    if end_date:
        query = query.where(Inventory.date <= end_date)
    result = await db.execute(query)
    return list(result.scalars().all())

async def adjust_inventory(
    db: AsyncSession,
    hotel_id: int,
    room_type: str,
    date: date,
    num_rooms: int = 1
) -> bool:
    # Find the inventory row with the latest date <= requested date
    query = (
        select(Inventory)
        .where(
            Inventory.hotel_id == hotel_id,
            Inventory.room_type == room_type,
            Inventory.date <= date,
            Inventory.available_rooms >= num_rooms
        )
        .order_by(desc(Inventory.date))
        .limit(1)
        .options(selectinload(Inventory.hotel))
    )
    result = await db.execute(query)
    inventory_row = result.scalars().first()
    if not inventory_row:
        return False

    # Decrement available_rooms on the ORM instance
    current_rooms = getattr(inventory_row, "available_rooms", None)
    if current_rooms is None:
        return False
    setattr(inventory_row, "available_rooms", current_rooms - num_rooms)
    await db.commit()
    return True

async def get_hotel_name_by_id(db: AsyncSession, hotel_id: int) -> Optional[str]:
    result = await db.execute(select(Hotel.hotel_name).where(Hotel.hotel_id == hotel_id))
    hotel_name = result.scalar_one_or_none()
    return hotel_name
