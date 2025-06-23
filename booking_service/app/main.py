from fastapi import FastAPI
from .api import booking
from .db.connection import engine
from .db.models import Base

app = FastAPI(
    title="Booking Service"
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(booking.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Booking Service"}