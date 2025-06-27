# Booking Service

This service handles the creation and management of customer bookings for the Hotel Inventory and Booking System.

## API Endpoints

- **`GET /bookings/`**: Retrieves a list of all bookings. Each booking includes the hotel name (fetched from the inventory service) and guest name is always masked as `[REDACTED]` for privacy.
- **`POST /bookings/`**: Creates a new booking. Checks inventory for the selected hotel and room type, fetches the room price, and masks guest name in the response. Adjusts inventory after booking.
    - **Body**: `BookingCreate` schema.
- **`GET /bookings/{booking_id}`**: Retrieves a specific booking by its ID, with hotel name lookup and guest name masked.
- **`PATCH /bookings/{booking_id}`**: Partially updates a booking. Only certain fields can be updated. Returns 400 if the booking is cancelled.
    - **Body**: Partial `BookingUpdate` schema.
- **`DELETE /bookings/{booking_id}`**: Cancels a booking. Sets the booking's `reservation_status` to `cancelled` and returns the updated booking. Adjusts inventory accordingly.
    - Returns 400 if the booking is already cancelled.

## Booking Logic
- **Inventory Check:** On booking creation, the service checks the inventory for the hotel and room type, and fetches the current room price.
- **PII Masking:** Guest names are always masked as `[REDACTED]` in API responses.
- **Hotel Name Lookup:** The service fetches the hotel name from the inventory service for each booking.
- **Inventory Adjustment:** Inventory is decremented on booking and incremented on cancellation or checkout.

## Monitoring & Observability
- **OpenTelemetry** for distributed tracing
- **Prometheus** for metrics
- **Loki** for logs
- **Grafana** for dashboards

## Development
To run the booking service directly (without Docker):
```bash
cd booking_service/app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
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
