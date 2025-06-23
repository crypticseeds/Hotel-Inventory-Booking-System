# Hotel Inventory and Booking System

This project is a microservices-based application for managing hotel inventory and bookings. It's designed to be scalable and maintainable, with a clear separation of concerns between services.

## Project Architecture

The application is composed of three main components:

-   `gateway/`: An API Gateway that acts as a single entry point for all incoming requests and routes them to the appropriate backend service.
-   `inventory_service/`: Manages hotel room availability, pricing, and hotel information.
-   `booking_service/`: Handles the creation and management of customer bookings.

Each service is a standalone FastAPI application, containerized with Docker.

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose

### Running the Application

To build and run the entire application stack, execute the following command from the project root:

```bash
docker-compose up --build
```

The services will be accessible at these endpoints:

-   **API Gateway**: `http://localhost:8080`
-   **Booking Service**: `http://localhost:8001`
-   **Inventory Service**: `http://localhost:8002`

## API Endpoints

The API Gateway routes requests to the appropriate service based on the path.

> **Note:** The current implementation of the API endpoints contains placeholder logic. The documentation below describes the intended functionality based on the defined schemas.

### Inventory Service (`/inventory`)

-   **`GET /inventory/`**: Retrieves a list of all inventory items.
-   **`POST /inventory/`**: Creates a new inventory item.
    -   **Body**: `InventoryCreate` schema.
-   **`GET /inventory/{item_id}`**: Retrieves a specific inventory item.

### Booking Service (`/bookings`)

-   **`GET /bookings/`**: Retrieves a list of all bookings.
-   **`POST /bookings/`**: Creates a new booking.
    -   **Body**: `BookingCreate` schema.
-   **`GET /bookings/{booking_id}`**: Retrieves a specific booking by its ID.

## How to Use

Here are some example `curl` commands to interact with the API via the gateway:

**Check inventory:**
```bash
curl http://localhost:8080/inventory/
```

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
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Make sure you have all dependencies installed. Install `uvicorn` and other dependencies using `pip` or `uv`:

```bash
pip install uvicorn
# or
uv pip install uvicorn
```

**Do not use `apt install uvicorn` for Python projects.**

## Database Schema

The application uses a PostgreSQL database for each service. The schemas are defined using SQLAlchemy.

### Inventory Service

-   **`hotel` table**: Stores information about hotels.
    -   `hotel_id` (Integer, PK): Unique identifier for the hotel.
    -   `hotel_name` (String): Name of the hotel.
    -   `location` (String): Location of the hotel.

-   **`inventory` table**: Manages room inventory for each hotel.
    -   `inventory_id` (Integer, PK): Unique identifier for the inventory record.
    -   `hotel_id` (Integer, FK): Foreign key to the `hotel` table.
    -   `room_type` (String): Type of the room (e.g., "deluxe", "suite").
    -   `date` (Date): The date for which the inventory is recorded.
    -   `available_rooms` (Integer): Number of available rooms.
    -   `room_price` (Numeric): Price of the room.
    -   `demand_level` (String, nullable): The forecasted demand level.

### Booking Service

-   **`booking` table**: Stores booking information.
    -   `booking_id` (UUID, PK): Unique identifier for the booking.
    -   `guest_name`
    -   `hotel_id` (Integer, FK): Foreign key to the `hotel` table.
    -   `arrival_date` (Date): Arrival date for the booking.
    -   `stay_length` (Integer): Number of nights.
    -   `check_out_date` (Date, Computed): Calculated as `arrival_date + stay_length`.
    -   `room_type` (String): Type of room booked.
    -   `adults` (Integer): Number of adults.
    -   `children` (Integer): Number of children.
    -   `meal_plan` (String, nullable): Meal plan for the booking.
    -   `market_segment` (String, nullable): Market segment of the booking.
    -   `is_weekend` (Boolean): True if the booking includes a weekend.
    -   `is_holiday` (Boolean): True if the booking is over a holiday.
    -   `booking_channel` (String, nullable): Channel through which the booking was made.
    -   `room_price` (Numeric): Price of the room for the booking.
    -   `reservation_status` (String): Status of the reservation (e.g., "confirmed", "cancelled").
    -   `created_at` (TIMESTAMP): Timestamp of when the booking was created.
