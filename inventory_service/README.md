# Inventory Service

This service manages hotel room availability, pricing, and hotel information for the Hotel Inventory and Booking System.

## API Endpoints

- **`GET /inventory/`**: Retrieves a list of all inventory items (sample data).
- **`GET /inventory/{hotel_id}`**: Retrieves all available rooms for a specific hotel. Supports optional `start_date` and `end_date` query parameters. Returns hotel name and location for each item.
- **`GET /inventory/hotel_name/{hotel_id}`**: Retrieves the hotel name for a given hotel ID.
- **`POST /inventory/{hotel_id}/adjust`**: Adjusts inventory for a hotel, room type, and date. Decrements or increments available rooms based on the request.

## Inventory Logic
- **Flexible Inventory Date Handling:** Inventory rows represent the start date of availability for a room type. Adjustments are made based on booking or cancellation.
- **Hotel Name Lookup:** Provides hotel name and location in responses and for use by other services.

## Monitoring & Observability
- **OpenTelemetry** for distributed tracing
- **Prometheus** for metrics
- **Loki** for logs
- **Grafana** for dashboards

## Development
To run the inventory service directly (without Docker):
```bash
cd inventory_service/app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Dependency Management Policy: Use UV
All Python dependency management must use [UV](https://docs.astral.sh/uv):
```bash
uv venv .venv
uv pip install -r requirements.txt
```

## Database Schema
The application uses PostgreSQL with SQLAlchemy ORM. See `db/models.py` for details.

---
For more information, see the root [README](../README.md).
