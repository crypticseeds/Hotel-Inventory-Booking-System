from fastapi import FastAPI
from .api import inventory

app = FastAPI(
    title="Inventory Service"
)

app.include_router(inventory.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Inventory Service"} 