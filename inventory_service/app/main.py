from fastapi import FastAPI
from .api import inventory
from .db.connection import engine, AsyncSessionLocal
from .db.models import Base
from .sample_data import populate_sample_inventory

app = FastAPI(
    title="Inventory Service"
)

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Populate sample data
    async with AsyncSessionLocal() as session:
        await populate_sample_inventory(session)

app.include_router(inventory.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory Service"} 