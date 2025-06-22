# Hotel Inventory and Booking System

This project is a microservices-based application for managing hotel inventory and bookings. It consists of two main services, an inventory service and a booking service, with an API gateway acting as a single entry point.

## Project Structure

The project is organized into the following directories:

-   `gateway/`: The API gateway that routes requests to the appropriate service.
-   `booking_service/`: The service for managing bookings.
-   `inventory_service/`: The service for managing hotel room inventory.
-   `shared/`: For shared utilities or libraries between services.

## Prerequisites

-   Docker
-   Docker Compose

## Running the Application

To run the entire application stack, use Docker Compose:

```bash
docker-compose up --build
```

This command will build the Docker images for each service and start the containers.

The services will be available at the following endpoints:

-   **API Gateway**: `http://localhost:8080`
    -   Booking requests: `http://localhost:8080/booking/...`
    -   Inventory requests: `http://localhost:8080/inventory/...`
-   **Booking Service** (direct access for testing): `http://localhost:8001`
-   **Inventory Service** (direct access for testing): `http://localhost:8002`

When to consider Traefik/NGINX later:
When you want to offload TLS, rate-limiting, and request routing to infra tools.

When preparing for full Kubernetes ingress-style routing.