import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from fastapi import FastAPI
from .api import inventory
from .db.connection import engine, AsyncSessionLocal
from .db.models import Base
from .sample_data import populate_sample_inventory

sentry_sdk.init(
    dsn="https://83433629f852f978cdd9a00d9bef78e6@o4509558402318336.ingest.de.sentry.io/4509558404677712",  # Same DSN as booking_service
    send_default_pii=True,
    traces_sample_rate=1.0,
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
)

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

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0 