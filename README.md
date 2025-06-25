# Hotel Inventory and Booking System

This project is a microservices-based application for managing hotel inventory and bookings. It's designed to be scalable and maintainable, with a clear separation of concerns between services.

## Tools Used
- FastAPI
- Sentry
- PostgreSQL (Neon Postgres)
- Uvicorn
- Docker & Docker Compose

## Project Architecture

The application is composed of three main components:

-   `gateway/`: An API Gateway that acts as a single entry point for all incoming requests and routes them to the appropriate backend service.
-   `inventory_service/`: Manages hotel room availability, pricing, and hotel information.
-   `booking_service/`: Handles the creation and management of customer bookings.

Each service is a standalone FastAPI application, containerized with Docker.

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Running the Application
To build and run the entire application stack, execute the following command from the project root:

```bash
docker-compose up --build
```

The services will be accessible at these endpoints:
- **API Gateway**: `http://localhost:8080`
- **Booking Service**: `http://localhost:8001`
- **Inventory Service**: `http://localhost:8002`

## Service Details

For detailed information about each service, including API endpoints, database schema, and service-specific logic, please refer to the respective README files:
- [Booking Service](./booking_service/README.md)
- [Inventory Service](./inventory_service/README.md)

## Future Enhancements
- Enforce idempotency for POST /booking to avoid duplicates.
- Service-to-service communication via message broker (e.g., Kafka, EventBridge).

---

For more information on contributing, troubleshooting, or advanced configuration, see the service-specific documentation. 