import time
from datetime import date as dt_date
# import os

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request, Response
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from sqlalchemy import select

from .api import booking
from .db.connection import engine
from .db.models import Base
from .monitoring import request_counter, request_duration_histogram, resource

app = FastAPI(title="Booking Service")

FastAPIInstrumentor.instrument_app(app)


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Start APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(return_rooms_after_checkout, "interval", days=1)
    scheduler.start()


app.include_router(booking.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Booking Service"}


# @app.get("/pricing/{hotel_id}")
# async def get_dynamic_pricing(hotel_id: int, room_type: str = "Standard", lead_time: int = 30):
#     """Get dynamic pricing from ML API"""
#     pricing_api_url = os.getenv('PRICING_API_URL', 'https://your-api-gateway-url/pricing')
    
#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(
#                 pricing_api_url,
#                 json={
#                     'hotel_id': hotel_id,
#                     'room_type': room_type,
#                     'lead_time': lead_time,
#                     'stay_length': 2,
#                     'adults': 2,
#                     'children': 0
#                 },
#                 timeout=5.0
#             )
            
#             if response.status_code == 200:
#                 return response.json()
#             else:
#                 return {"error": "Pricing service unavailable", "fallback_price": 100.0}
                
#         except Exception as e:
#             return {"error": str(e), "fallback_price": 100.0}


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    labels = {
        "service": resource.attributes.get("service.name", "unknown"),
        "method": request.method,
        "path": request.url.path,
    }
    start_time = time.time()
    try:
        response: Response = await call_next(request)
        duration = time.time() - start_time
        request_duration_histogram.record(duration, labels)
        request_counter.add(1, {**labels, "status_code": str(response.status_code)})
        return response
    except Exception:
        duration = time.time() - start_time
        request_duration_histogram.record(duration, labels)
        request_counter.add(1, {**labels, "status_code": "500"})
        raise


default_return_rooms_after_checkout = None
try:
    default_return_rooms_after_checkout = return_rooms_after_checkout
except NameError:
    pass


def return_rooms_after_checkout():
    from .db.connection import AsyncSessionLocal
    from .db.models import Booking as BookingModel

    async def _return_rooms():
        async with AsyncSessionLocal() as db:
            # Find bookings with check_out_date < today and reservation_status == 'confirmed'
            result = await db.execute(
                select(BookingModel).where(
                    BookingModel.check_out_date < dt_date.today(),
                    BookingModel.reservation_status == "confirmed",
                )
            )
            bookings = result.scalars().all()
            for booking in bookings:
                # Call inventory service to increment available_rooms
                inventory_service_url = "https://inventory-service.inventory.svc.cluster.local:8000"
                adjust_url = f"{inventory_service_url}/{booking.hotel_id}/adjust"
                adjust_payload = {
                    "room_type": booking.room_type,
                    "date": str(booking.arrival_date),  # Use arrival_date as reference
                    "num_rooms": -1,  # -1 to increment (reverse of booking)
                }
                async with httpx.AsyncClient() as client:
                    try:
                        await client.post(adjust_url, json=adjust_payload, timeout=5.0)
                    except Exception:
                        pass  # Optionally log error
                # Update booking status to 'checked-out'
                booking.reservation_status = "checked-out"
            await db.commit()

    return _return_rooms
