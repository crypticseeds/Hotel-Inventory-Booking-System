import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from fastapi import FastAPI
from .api import booking
from .db.connection import engine
from .db.models import Base

sentry_sdk.init(
    dsn="https://83433629f852f978cdd9a00d9bef78e6@o4509558402318336.ingest.de.sentry.io/4509558404677712",  # TODO: Replace with your actual DSN
    send_default_pii=True,
    traces_sample_rate=1.0,
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
)

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