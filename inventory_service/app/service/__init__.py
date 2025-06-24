from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date
from ..db.models import Inventory, Hotel
from sqlalchemy.orm import selectinload

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
