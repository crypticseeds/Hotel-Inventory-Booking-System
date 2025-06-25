# Inventory Service

This service manages hotel room availability, pricing, and hotel information for the Hotel Inventory and Booking System.

## API Endpoints

- **`GET /inventory/`**: Retrieves a list of all inventory items.
- **`POST /inventory/`**: Creates a new inventory item.
    - **Body**: `InventoryCreate` schema.
- **`GET /inventory/{item_id}`**: Retrieves a specific inventory item.
- **`GET /inventory/{hotel_id}`**: Retrieves all available rooms for a specific hotel. Returns a list of inventory items for the given hotel, each including:
    - `hotel_id`: The unique hotel identifier
    - `hotel_name`: The name of the hotel
    - `location`: The location of the hotel
    - `room_type`: The type of room (e.g., "deluxe", "suite")
    - `date`: The date for which the inventory is available
    - `available_rooms`: Number of available rooms of that type
    - `room_price`: Price of the room
    - `demand_level`: The forecasted demand level (if available)
    - Supports optional query parameters `start_date` and `end_date` (YYYY-MM-DD) to filter inventory by date range.
    - Example:
      ```bash
      curl "http://localhost:8002/inventory/111?start_date=2024-06-01&end_date=2024-06-30"
      ```

**Check inventory via gateway:**
```bash
curl http://localhost:8080/inventory/
```

## Database Schema

The application uses a PostgreSQL database. The schema is defined using SQLAlchemy.

### Inventory Service

- **`hotel` table**: Stores information about hotels.
    - `hotel_id` (Integer, PK): Unique identifier for the hotel.
    - `hotel_name` (String): Name of the hotel.
    - `location` (String): Location of the hotel.

- **`inventory` table**: Manages room inventory for each hotel.
    - `hotel_id` (Integer, FK): Foreign key to the `hotel` table.
    - `room_type` (String): Type of the room (e.g., "deluxe", "suite").
    - `date` (Date): The **start date** for which the inventory is available. This date is now interpreted as the beginning of ongoing availability for that room type.
    - `available_rooms` (Integer): Number of available rooms. This value is decremented for bookings on or after the start date.
    - `room_price` (Numeric): Price of the room.
    - `demand_level` (String, nullable): The forecasted demand level.

## Inventory Adjustment Logic

### Flexible Inventory Date Handling

- **Inventory rows represent the start date of availability for a room type.**
- When a booking is made for a date on or after the inventory's `date`, the system will decrement `available_rooms` from the inventory row with the latest `date` less than or equal to the booking date.
- **You do not need to create a row for every date.** A single row with a start date is sufficient for ongoing availability.

#### Example
Suppose you have this inventory row:

| hotel_id | room_type     | date       | available_rooms |
|----------|--------------|------------|----------------|
| 111      | Deluxe Rooms  | 2024-07-01 | 5              |

If a booking is made for `2024-07-03`, the system will decrement `available_rooms` in the row for `2024-07-01` (since that's the start of availability).

If a booking is made for `2024-07-01`, `2024-07-02`, or any future date, the same row will be used (as long as `available_rooms` is sufficient).

### API Changes
- The `POST /inventory/{hotel_id}/adjust` endpoint now finds the correct inventory row based on this logic.
- If no suitable row is found (e.g., all are in the future or have insufficient rooms), a 400 error is returned.

## Running the Inventory Service for Development

To run the inventory service directly (without Docker), navigate to the `inventory_service/app` directory and run:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Make sure you have all dependencies installed. Install `uvicorn` and other dependencies using `pip` or `uv`:

```bash
pip install uvicorn
# or
uv pip install uvicorn
```

**Do not use `apt install uvicorn` for Python projects.**
