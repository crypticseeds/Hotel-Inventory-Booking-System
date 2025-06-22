from fastapi import APIRouter

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
)

@router.get("/")
async def read_inventory():
    return [{"item": "deluxe room", "quantity": 10}, {"item": "suite", "quantity": 5}]

@router.get("/{item_id}")
async def read_inventory_item(item_id: str):
    return {"item": item_id, "quantity": 1} 