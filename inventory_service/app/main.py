import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from fastapi import FastAPI
from .api import inventory
from .db.connection import engine, AsyncSessionLocal
from .db.models import Base
from .sample_data import populate_sample_inventory
import logging
from pythonjsonlogger import jsonlogger
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import trace
import os

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

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        record.service = 'inventory-service'
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
otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://localhost:4317')
resource = Resource(attributes={SERVICE_NAME: 'inventory-service'})
provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)
trace.set_tracer_provider(provider)

# Instrument logging and FastAPI
LoggingInstrumentor().instrument(set_logging_format=False)

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
