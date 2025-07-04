import logging
import os

import sentry_sdk
from opentelemetry import _logs, trace
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.metrics import get_meter, set_meter_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pythonjsonlogger import jsonlogger
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

# --- Logging Setup ---
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PiiFilter(logging.Filter):
    def filter(self, record):
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
root_logger.handlers = []
root_logger.addHandler(log_handler)
root_logger.setLevel(logging.DEBUG)

class ServiceLogFilter(logging.Filter):
    def filter(self, record):
        record.service = 'inventory-service'
        span = trace.get_current_span()
        if span and span.get_span_context().is_valid:
            record.trace_id = format(span.get_span_context().trace_id, '032x')
            record.span_id = format(span.get_span_context().span_id, '016x')
        else:
            record.trace_id = None
            record.span_id = None
        return True
root_logger.addFilter(ServiceLogFilter())

# --- Tracing Setup ---
otlp_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'otel-collector.observability.svc.cluster.local:4317')
resource = Resource(attributes={SERVICE_NAME: 'inventory-service'})
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
LoggingInstrumentor().instrument(set_logging_format=False)

# --- Metrics Setup ---
metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=60000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
set_meter_provider(meter_provider)
meter = get_meter(__name__)

request_duration_histogram = meter.create_histogram(
    name="http_request_duration_seconds",
    description="Duration of HTTP requests in seconds",
    unit="s"
)
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)
db_connection_errors_counter = meter.create_counter(
    name="db_connection_errors_total",
    description="Total number of DB connection errors",
    unit="1"
)

# --- Sentry Setup ---
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    send_default_pii=True,
    traces_sample_rate=1.0,
    integrations=[
        StarletteIntegration(transaction_style="endpoint"),
        FastApiIntegration(transaction_style="endpoint"),
    ],
) 