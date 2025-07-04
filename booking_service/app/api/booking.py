import logging
from datetime import timedelta

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..db.connection import get_db
from ..db.models import Booking as BookingModel
from ..monitoring import (
    booking_failure_ratio_counter,
    db_connection_errors_counter,
    resource,
)
from ..schemas import Booking, BookingCreate, BookingUpdate

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/bookings",
    tags=["bookings"],
)

# Utility to mask PII in dicts
PII_FIELDS = ["guest_name"]


def mask_pii(data):
    if isinstance(data, dict):
        return {k: ("[REDACTED]" if k in PII_FIELDS else v) for k, v in data.items()}
    return data


@router.get("/", response_model=list[Booking])
async def read_bookings(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(BookingModel))
        bookings = result.scalars().all()
        inventory_service_url = "http://inventory-service.inventory.svc.cluster.local:8000/inventory"
        booking_list = []
        async with httpx.AsyncClient() as client:
            for db_booking in bookings:
                hotel_name = None
                hotel_name_url = (
                    f"{inventory_service_url}/hotel_name/{db_booking.hotel_id}"
                )
                try:
                    hotel_resp = await client.get(hotel_name_url, timeout=5.0)
                    if hotel_resp.status_code == 200:
                        hotel_name = hotel_resp.json().get("hotel_name")
                except Exception as e:
                    logger.warning(
                        f"Error fetching hotel name for booking {db_booking.booking_id}: {e}"
                    )
                booking_data = {
                    "booking_id": db_booking.booking_id,
                    "guest_name": "[REDACTED]",  # Mask PII
                    "hotel_name": hotel_name,
                    "arrival_date": db_booking.arrival_date,
                    "stay_length": db_booking.stay_length,
                    "check_out_date": db_booking.check_out_date,
                    "room_type": db_booking.room_type,
                    "adults": db_booking.adults,
                    "children": db_booking.children,
                    "meal_plan": db_booking.meal_plan,
                    "market_segment": db_booking.market_segment,
                    "is_holiday": db_booking.is_holiday,
                    "booking_channel": db_booking.booking_channel,
                    "room_price": db_booking.room_price,
                    "total_price": float(db_booking.room_price) * db_booking.stay_length
                    if db_booking.room_price is not None
                    and db_booking.stay_length is not None
                    else None,
                    "reservation_status": db_booking.reservation_status,
                    "created_at": db_booking.created_at.date()
                    if hasattr(db_booking.created_at, "date")
                    else db_booking.created_at,
                }
                booking_list.append(booking_data)
        return booking_list
    except Exception as e:
        logger.error(f"Error fetching bookings: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=Booking)
async def create_booking(booking: BookingCreate, db: AsyncSession = Depends(get_db)):
    try:
        logger.debug(f"Received booking data: {mask_pii(booking.dict())}")
        booking_dict = booking.dict()
        if "hotel_name" in booking_dict:
            booking_dict.pop("hotel_name")
        # Set reservation_status to 'confirmed' automatically
        booking_dict["reservation_status"] = "confirmed"
        # Automatically calculate is_weekend
        arrival = booking.arrival_date
        stay = booking.stay_length
        is_weekend = False
        for i in range(stay):
            day = arrival + timedelta(days=i)
            if day.weekday() in [5, 6]:  # Saturday=5, Sunday=6
                is_weekend = True
                break
        booking_dict["is_weekend"] = is_weekend

        # New inventory logic: fetch inventory for hotel and room type, ignore date
        inventory_service_url = "http://inventory-service.inventory.svc.cluster.local:8000/inventory"
        inventory_url = f"{inventory_service_url}/{booking.hotel_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(inventory_url)
            if resp.status_code == 200:
                inventory_list = resp.json()
                inventory_row = None
                for item in inventory_list:
                    if item["room_type"] == booking.room_type:
                        inventory_row = item
                        break
                if not inventory_row:
                    booking_failure_ratio_counter.add(
                        1,
                        {"service": resource.attributes.get("service.name", "unknown")},
                    )
                    raise HTTPException(
                        status_code=400,
                        detail="Room type not found in inventory for the given hotel.",
                    )
                # Check available_rooms and arrival_date
                from datetime import date as dt_date

                if inventory_row["available_rooms"] < 1:
                    booking_failure_ratio_counter.add(
                        1,
                        {"service": resource.attributes.get("service.name", "unknown")},
                    )
                    raise HTTPException(
                        status_code=400,
                        detail="No available rooms for the selected room type.",
                    )
                if booking.arrival_date < dt_date.today():
                    booking_failure_ratio_counter.add(
                        1,
                        {"service": resource.attributes.get("service.name", "unknown")},
                    )
                    raise HTTPException(
                        status_code=400, detail="Cannot book for a past date."
                    )
                booking_dict["room_price"] = inventory_row["room_price"]
            else:
                booking_failure_ratio_counter.add(
                    1, {"service": resource.attributes.get("service.name", "unknown")}
                )
                raise HTTPException(
                    status_code=400, detail="Failed to fetch inventory for room price."
                )

        # Do not set check_out_date, as it is a generated column
        db_booking = BookingModel(**booking_dict)
        logger.debug(f"Created booking model: {mask_pii(db_booking.__dict__)}")
        db.add(db_booking)
        await db.commit()
        await db.refresh(db_booking)
        booking_failure_ratio_counter.add(
            -1, {"service": resource.attributes.get("service.name", "unknown")}
        )

        # Adjust inventory for the booking (remove one room for the room type)
        adjust_payload = {
            "room_type": booking.room_type,
            "date": str(inventory_row["date"]),  # Use the date from inventory row
            "num_rooms": 1,
        }
        async with httpx.AsyncClient() as client:
            adjust_url = f"{inventory_service_url}/{booking.hotel_id}/adjust"
            try:
                resp = await client.post(adjust_url, json=adjust_payload, timeout=5.0)
                if resp.status_code != 200:
                    logger.warning(
                        f"Inventory adjustment failed for {adjust_payload}: {resp.text}"
                    )
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
            "guest_name": "[REDACTED]",  # Mask PII
            "hotel_name": hotel_name,
            "arrival_date": db_booking.arrival_date,
            "stay_length": db_booking.stay_length,
            "check_out_date": db_booking.check_out_date,
            "room_type": db_booking.room_type,
            "adults": db_booking.adults,
            "children": db_booking.children,
            "meal_plan": db_booking.meal_plan,
            "market_segment": db_booking.market_segment,
            "is_holiday": db_booking.is_holiday,
            "booking_channel": db_booking.booking_channel,
            "room_price": db_booking.room_price,
            "total_price": float(db_booking.room_price) * db_booking.stay_length
            if db_booking.room_price is not None and db_booking.stay_length is not None
            else None,
            "reservation_status": db_booking.reservation_status,
            "created_at": db_booking.created_at.date()
            if hasattr(db_booking.created_at, "date")
            else db_booking.created_at,
        }
        logger.debug(f"Final response data: {mask_pii(booking_data)}")
        return booking_data
    except Exception as e:
        logger.error(f"Error creating booking: {str(e)}", exc_info=True)
        try:
            await db.rollback()
        except Exception:
            db_connection_errors_counter.add(
                1, {"service": resource.attributes.get("service.name", "unknown")}
            )
        booking_failure_ratio_counter.add(
            1, {"service": resource.attributes.get("service.name", "unknown")}
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{booking_id}", response_model=Booking)
async def get_booking_by_id(
    booking_id: str = Path(..., description="The 7-character booking ID"),
    db: AsyncSession = Depends(get_db),
):
    try:
        db_booking = await db.get(BookingModel, booking_id)
        if not db_booking:
            raise HTTPException(status_code=404, detail="Booking not found")

        # Fetch hotel_name from inventory service
        inventory_service_url = "http://inventory-service.inventory.svc.cluster.local:8000/inventory"
        async with httpx.AsyncClient() as client:
            hotel_name_url = f"{inventory_service_url}/hotel_name/{db_booking.hotel_id}"
            hotel_resp = await client.get(hotel_name_url, timeout=5.0)
            if hotel_resp.status_code == 200:
                hotel_name = hotel_resp.json().get("hotel_name")
            else:
                hotel_name = None

        booking_data = {
            "booking_id": db_booking.booking_id,
            "guest_name": "[REDACTED]",  # Mask PII
            "hotel_name": hotel_name,
            "arrival_date": db_booking.arrival_date,
            "stay_length": db_booking.stay_length,
            "check_out_date": db_booking.check_out_date,
            "room_type": db_booking.room_type,
            "adults": db_booking.adults,
            "children": db_booking.children,
            "meal_plan": db_booking.meal_plan,
            "market_segment": db_booking.market_segment,
            "is_holiday": db_booking.is_holiday,
            "booking_channel": db_booking.booking_channel,
            "room_price": db_booking.room_price,
            "total_price": float(db_booking.room_price) * db_booking.stay_length
            if db_booking.room_price is not None and db_booking.stay_length is not None
            else None,
            "reservation_status": db_booking.reservation_status,
            "created_at": db_booking.created_at.date()
            if hasattr(db_booking.created_at, "date")
            else db_booking.created_at,
        }
        return booking_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching booking: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{booking_id}", response_model=Booking)
async def cancel_booking(
    booking_id: str = Path(..., description="The 7-character booking ID to cancel"),
    db: AsyncSession = Depends(get_db),
):
    try:
        db_booking = await db.get(BookingModel, booking_id)
        if not db_booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if str(getattr(db_booking, "reservation_status")).lower() == "cancelled":
            raise HTTPException(status_code=400, detail="Booking is already cancelled")

        # Mark as cancelled
        db_booking.reservation_status = "cancelled"  # type: ignore[attr-defined]
        await db.commit()
        await db.refresh(db_booking)

        # Return one room to inventory (for the entire stay)
        inventory_service_url = "http://inventory-service.inventory.svc.cluster.local:8000/inventory"
        adjust_payload = {
            "room_type": db_booking.room_type,
            "date": str(db_booking.arrival_date),
            "num_rooms": -1,
        }
        async with httpx.AsyncClient() as client:
            adjust_url = f"{inventory_service_url}/{db_booking.hotel_id}/adjust"
            try:
                resp = await client.post(adjust_url, json=adjust_payload, timeout=5.0)
                if resp.status_code != 200:
                    logger.warning(
                        f"Inventory adjustment (return) failed for {adjust_payload}: {resp.text}"
                    )
            except Exception as e:
                logger.warning(f"Error calling inventory service to return room: {e}")

        # Fetch hotel_name from inventory service
        async with httpx.AsyncClient() as client:
            hotel_name_url = f"{inventory_service_url}/hotel_name/{db_booking.hotel_id}"
            hotel_resp = await client.get(hotel_name_url, timeout=5.0)
            if hotel_resp.status_code == 200:
                hotel_name = hotel_resp.json().get("hotel_name")
            else:
                hotel_name = None

        booking_data = {
            "booking_id": db_booking.booking_id,
            "guest_name": "[REDACTED]",  # Mask PII
            "hotel_name": hotel_name,
            "arrival_date": db_booking.arrival_date,
            "stay_length": db_booking.stay_length,
            "check_out_date": db_booking.check_out_date,
            "room_type": db_booking.room_type,
            "adults": db_booking.adults,
            "children": db_booking.children,
            "meal_plan": db_booking.meal_plan,
            "market_segment": db_booking.market_segment,
            "is_holiday": db_booking.is_holiday,
            "booking_channel": db_booking.booking_channel,
            "room_price": db_booking.room_price,
            "total_price": float(db_booking.room_price) * db_booking.stay_length
            if db_booking.room_price is not None and db_booking.stay_length is not None
            else None,
            "reservation_status": db_booking.reservation_status,
            "created_at": db_booking.created_at.date()
            if hasattr(db_booking.created_at, "date")
            else db_booking.created_at,
        }
        return booking_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling booking: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: str = Path(..., description="The 7-character booking ID to update"),
    booking_update: BookingUpdate = Body(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        db_booking = await db.get(BookingModel, booking_id)
        if not db_booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if str(getattr(db_booking, "reservation_status")).lower() == "cancelled":
            raise HTTPException(
                status_code=400,
                detail="Booking has been cancelled and cannot be modified",
            )

        update_data = booking_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_booking, field, value)

        # Removed check_out_date update since it is a generated column

        await db.commit()
        await db.refresh(db_booking)

        # Fetch hotel_name from inventory service
        inventory_service_url = "http://inventory-service.inventory.svc.cluster.local:8000/inventory"
        async with httpx.AsyncClient() as client:
            hotel_name_url = f"{inventory_service_url}/hotel_name/{db_booking.hotel_id}"
            hotel_resp = await client.get(hotel_name_url, timeout=5.0)
            if hotel_resp.status_code == 200:
                hotel_name = hotel_resp.json().get("hotel_name")
            else:
                hotel_name = None

        booking_data = {
            "booking_id": db_booking.booking_id,
            "guest_name": "[REDACTED]",  # Mask PII
            "hotel_name": hotel_name,
            "arrival_date": db_booking.arrival_date,
            "stay_length": db_booking.stay_length,
            "check_out_date": db_booking.check_out_date,
            "room_type": db_booking.room_type,
            "adults": db_booking.adults,
            "children": db_booking.children,
            "meal_plan": db_booking.meal_plan,
            "market_segment": db_booking.market_segment,
            "is_holiday": db_booking.is_holiday,
            "booking_channel": db_booking.booking_channel,
            "room_price": db_booking.room_price,
            "total_price": float(db_booking.room_price) * db_booking.stay_length
            if db_booking.room_price is not None and db_booking.stay_length is not None
            else None,
            "reservation_status": db_booking.reservation_status,
            "created_at": db_booking.created_at.date()
            if hasattr(db_booking.created_at, "date")
            else db_booking.created_at,
        }
        return booking_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
