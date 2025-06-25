# Booking Service

This service handles the creation and management of customer bookings for the Hotel Inventory and Booking System.

## API Endpoints

- **`GET /bookings/`**: Retrieves a list of all bookings.
- **`POST /bookings/`**: Creates a new booking.
    - **Body**: `BookingCreate` schema.
- **`GET /bookings/{booking_id}`**: Retrieves a specific booking by its ID.
- **`PATCH /bookings/{booking_id}`**: Partially updates a booking. Only the following fields can be updated: `guest_name`, `arrival_date`, `stay_length`, `room_type`, `adults`, `children`.
    - **Body**: Partial `BookingUpdate` schema (only fields to be updated are required).
    - Returns 400 if the booking is cancelled.
    - Example:
      ```bash
      curl -X PATCH http://localhost:8080/bookings/{booking_id} \
        -H "Content-Type: application/json" \
        -d '{"guest_name": "Updated Name"}'
      ```
- **`DELETE /bookings/{booking_id}`**: Cancels a booking. Sets the booking's `reservation_status` to `cancelled` and returns the updated booking.
    - Returns 400 if the booking is already cancelled.
    - Example:
      ```bash
      curl -X DELETE http://localhost:8080/bookings/{booking_id}
      ```

## How to Use

Here are some example `curl` commands to interact with the API via the gateway:

**Create a booking (example payload):**
```bash
curl -X POST http://localhost:8080/bookings/ -H "Content-Type: application/json" -d '{
  "guest_name": "Femi A",
  "hotel_id": 1,
  "arrival_date": "2024-09-15",
  "stay_length": 2,
  "room_type": "deluxe",
  "adults": 2,
  "children": 0,
  "meal_plan": "breakfast",
  "market_segment": "online",
  "is_weekend": false,
  "is_holiday": false,
  "booking_channel": "web",
  "room_price": 250.00,
  "reservation_status": "confirmed"
}'
```

## Development vs Production Database Schema Changes

- During development, you may drop and recreate tables to pick up model changes. This will remove all data in the table, but ensures the schema matches your models.
- In production, **do not drop tables**. Instead, use a migration tool like Alembic to safely update your database schema without losing data.

## Running the Booking Service for Development

To run the booking service directly (without Docker), navigate to the `booking_service/app` directory and run:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

Make sure you have all dependencies installed. Install `uvicorn` and other dependencies using `pip` or `uv`:

```bash
pip install uvicorn
# or
uv pip install uvicorn
```

**Do not use `apt install uvicorn` for Python projects.**

## Database Schema

The application uses a PostgreSQL database. The schema is defined using SQLAlchemy.

### Booking Service

- **`booking` table**: Stores booking information.
    - `booking_id` (UUID, PK): Unique identifier for the booking.
    - `guest_name`
    - `hotel_id` (Integer, FK): Foreign key to the `hotel` table.
    - `arrival_date` (Date): Arrival date for the booking.
    - `stay_length` (Integer): Number of nights.
    - `check_out_date` (Date, Computed): Calculated as `arrival_date + stay_length`.
    - `room_type` (String): Type of room booked.
    - `adults` (Integer): Number of adults.
    - `children` (Integer): Number of children.
    - `meal_plan` (String, nullable): Meal plan for the booking.
    - `market_segment` (String, nullable): Market segment of the booking.
    - `is_weekend` (Boolean): True if the booking includes a weekend.
    - `is_holiday` (Boolean): True if the booking is over a holiday.
    - `booking_channel` (String, nullable): Channel through which the booking was made.
    - `room_price` (Numeric): Price of the room for the booking.
    - `reservation_status` (String): Status of the reservation (e.g., "confirmed", "cancelled").
    - `created_at` (TIMESTAMP): Timestamp of when the booking was created.
