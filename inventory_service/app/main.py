from fastapi import FastAPI
from .api import inventory
from .db.connection import engine
from .db.models import Base

app = FastAPI(
    title="Inventory Service"
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(inventory.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory Service"} 