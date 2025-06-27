from .monitoring import logger, resource, request_duration_histogram, request_counter, db_connection_errors_counter
from fastapi import FastAPI, Request, Response
from .api import inventory
from .db.connection import engine, AsyncSessionLocal
from .db.models import Base
from .sample_data import populate_sample_inventory
import time
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI(
    title="Inventory Service"
)

FastAPIInstrumentor.instrument_app(app)

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
    except Exception as e:
        duration = time.time() - start_time
        request_duration_histogram.record(duration, labels)
        request_counter.add(1, {**labels, "status_code": "500"})
        raise

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
