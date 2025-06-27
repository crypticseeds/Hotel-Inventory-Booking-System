import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from fastapi import FastAPI
from .api import booking
from .db.connection import engine
from .db.models import Base
import logging
from pythonjsonlogger import jsonlogger
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import trace
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry import _logs
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.future import select
import httpx
from datetime import date as dt_date

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
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
    # Start APScheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(return_rooms_after_checkout, 'interval', days=1)
    scheduler.start()

app.include_router(booking.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Booking Service"}

# --- Structured Logging Setup ---
class PiiFilter(logging.Filter):
    def filter(self, record):
        # Remove or mask PII fields from log records
        if hasattr(record, 'guest_name'):
            record.guest_name = '[REDACTED]'
        return True

log_handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(name)s %(message)s %(service)s %(trace_id)s %(span_id)s'
)
log_handler.setFormatter(formatter)
log_handler.addFilter(PiiFilter())
root_logger = logging.getLogger()
root_logger.handlers = []  # Remove default handlers
root_logger.addHandler(log_handler)
root_logger.setLevel(logging.DEBUG)  # Capture all levels during development

# Add 'service' field to all logs
class ServiceLogFilter(logging.Filter):
    def filter(self, record):
        record.service = 'booking-service'
        # Add trace/span context if available
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            record.trace_id = format(span.get_span_context().trace_id, '032x')
            record.span_id = format(span.get_span_context().span_id, '016x')
        else:
            record.trace_id = None
            record.span_id = None
        return True
root_logger.addFilter(ServiceLogFilter())

# --- OpenTelemetry Tracing Setup ---
otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://otel-collector:4317')
resource = Resource(attributes={SERVICE_NAME: 'booking-service'})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

# --- OpenTelemetry Logging Setup ---
otlp_log_exporter = OTLPLogExporter(endpoint=otlp_endpoint, insecure=True)
log_provider = LoggerProvider(resource=resource)
log_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
_logs.set_logger_provider(log_provider)

otel_handler = LoggingHandler(level=logging.NOTSET, logger_provider=log_provider)
root_logger.addHandler(otel_handler)

# Instrument logging and FastAPI
LoggingInstrumentor().instrument(set_logging_format=False)

async def return_rooms_after_checkout():
    from .db.connection import AsyncSessionLocal
    from .db.models import Booking as BookingModel
    async with AsyncSessionLocal() as db:
        # Find bookings with check_out_date < today and reservation_status == 'confirmed'
        result = await db.execute(
            select(BookingModel).where(
                BookingModel.check_out_date < dt_date.today(),
                BookingModel.reservation_status == 'confirmed'
            )
        )
        bookings = result.scalars().all()
        for booking in bookings:
            # Call inventory service to increment available_rooms
            inventory_service_url = "http://inventory_service:8000/inventory"
            adjust_url = f"{inventory_service_url}/{booking.hotel_id}/adjust"
            adjust_payload = {
                "room_type": booking.room_type,
                "date": str(booking.arrival_date),  # Use arrival_date as reference
                "num_rooms": -1  # -1 to increment (reverse of booking)
            }
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(adjust_url, json=adjust_payload, timeout=5.0)
                except Exception as e:
                    pass  # Optionally log error
            # Update booking status to 'completed'
            booking.reservation_status = 'completed'
        await db.commit()