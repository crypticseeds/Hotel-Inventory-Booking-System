from fastapi import FastAPI
from .api import booking

app = FastAPI(
    title="Booking Service"
)

app.include_router(booking.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Booking Service"} 