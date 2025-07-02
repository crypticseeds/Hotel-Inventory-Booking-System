# Learnings & Challenges: Microservice Database Integrity

This document captures the key challenges and learnings encountered while building out the booking service and ensuring data integrity with the existing inventory service.

## 1. The Challenge: Foreign Key to a Composite Key

**Initial Goal:** To have the `booking` table's `hotel_id` reference the `inventory` table to ensure that every booking corresponds to a valid hotel.

**Problem:** The `inventory` table used a composite primary key (`hotel_id`, `room_type`, `date`). A fundamental rule of relational databases is that a foreign key must reference the *entire* primary key of another table. It was therefore impossible to create a foreign key from `booking.hotel_id` to just the `hotel_id` part of the `inventory` primary key.

## 2. The Solution: Database Refactoring

**Proposed Solution:** To resolve the issue, a database refactoring was proposed:

1.  **Introduce a `hotel` Table:** Create a new `hotel` table with a single-column primary key (e.g., an auto-incrementing `hotel_id`). This table holds information about each hotel.
2.  **Update `inventory` Table:** Modify the `inventory` table to remove the composite key and instead include a foreign key that references the new `hotel` table's `hotel_id`.
3.  **Update `booking` Table:** The `booking` table can now be created with a simple, clean foreign key that also references `hotel.hotel_id`.

This approach normalizes the database schema and establishes robust, clear relationships between the entities.

## 3. Key Takeaways

*   **Database Design:** Avoid composite primary keys when other tables will need to reference only a part of that key. Using a single, auto-generated surrogate key (like `Identity` or `SERIAL`) is often a more flexible and scalable approach.
*   **Microservice Architecture:** When microservices share a single database, you can and should use database-level constraints (like foreign keys) to enforce data integrity.
*   **Communication:** Clearly explaining the "why" behind a technical decision is critical. A proposed refactor can be misinterpreted if the underlying problem (e.g., the composite key constraint) isn't communicated effectively.

## 4. Inventory Service Schema & Async Setup

This section details the creation of the database schema for the `inventory_service` and the setup of its asynchronous connection to a PostgreSQL database.

**Work Completed:**

*   **Database Schema:** A new table, `inventory`, was defined using **SQLAlchemy ORM**. It features a composite primary key (`hotel_id`, `room_type`, `date`) to ensure unique daily availability records and an index on `location` and `date` to optimize searches.
*   **Data Validation:** **Pydantic** models were implemented to ensure the integrity and structure of incoming data.
*   **Async Connection:** The service was configured to connect to the database asynchronously using the **`asyncpg`** driver. The FastAPI application now automatically creates the database schema on startup if it doesn't exist.
*   **Environment:** Dependencies were managed using **`uv`**, and environment variables for the database URL were handled with **`python-dotenv`**.

**Key Learnings & Challenges:**

*   **SQLAlchemy Driver Specificity:** A significant challenge was a `ModuleNotFoundError` for `psycopg2`, even though `asyncpg` was the intended driver.
    *   **Learning:** SQLAlchemy defaults to `psycopg2` for `postgresql://` connection strings. To use `asyncpg`, the URL **must** be explicitly defined as `postgresql+asyncpg://...`. This small detail is critical for async operations to function correctly.
*   **Network vs. Code Errors:** An `OSError: Network is unreachable` was encountered.
    *   **Learning:** This reinforced that errors are not always in the application code. The issue was a network connectivity problem between the service and the database, solvable by correcting the database URL or firewall settings, not by changing Python code.
*   **Python Imports in Packages:** An initial `ModuleNotFoundError` for `app.models` highlighted a common pitfall.
    *   **Learning:** When working within a Python package (like our `app`), using relative imports (`from . import module`) is crucial for modules to correctly find each other.

## 5. API Endpoints Overview

### Booking Service (`/bookings`)
- **GET /bookings/**: List all bookings.
- **POST /bookings/**: Create a new booking.
- **GET /bookings/{booking_id}**: Retrieve a booking by its UUID.
- **PATCH /bookings/{booking_id}**: Update fields of a booking (guest_name, arrival_date, stay_length, room_type, adults, children).
- **DELETE /bookings/{booking_id}**: Cancel a booking (sets reservation_status to 'cancelled').

### Inventory Service (`/inventory`)
- **GET /inventory/**: List all inventory items (sample data or stub).
- **GET /inventory/{hotel_id}**: List inventory for a specific hotel, with optional date range.
- **GET /inventory/hotel_name/{hotel_id}**: Get the hotel name for a given hotel_id.
- **POST /inventory/{hotel_id}/adjust**: Adjust inventory for a hotel (decrement/increment available rooms).

### API Gateway
- **/booking/{path:path}**: Proxies all booking-related requests to the booking service.
- **/inventory/{path:path}**: Proxies all inventory-related requests to the inventory service.
- **GET /**: Health check for the gateway.

## 6. Libraries, Tools, and Core FastAPI Functions

### Main Libraries & Tools
- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database models and async database access.
- **asyncpg**: Async PostgreSQL driver.
- **psycopg2-binary**: (Fallback/legacy) PostgreSQL driver.
- **Pydantic**: Data validation and settings management.
- **python-dotenv**: Loads environment variables from `.env` files.
- **httpx**: Async HTTP client for service-to-service calls.
- **faker**: Generates fake data for sample inventory.
- **uv**: Fast dependency and environment manager (used in Docker setup).
- **Docker & Docker Compose**: Containerization and orchestration.

### Core FastAPI Functions/Classes Used
- `FastAPI`: Main app instance.
- `APIRouter`: For modular route definitions.
- `@app.get`, `@app.post`, `@app.patch`, `@app.delete`, `@app.on_event`: Route and event decorators.
- `Depends`: Dependency injection (e.g., for DB sessions).
- `HTTPException`: For error handling and custom responses.
- `Body`, `Query`, `Path`: For request data validation and extraction.
- `Request`, `Response`: For low-level request/response handling (used in gateway).

### Other Notable Imports
- `sqlalchemy.ext.asyncio`: Async database engine/session.
- `sqlalchemy.orm`: ORM base and session management.
- `sqlalchemy.future.select`: Async query building.
- `sqlalchemy.dialects.postgresql.UUID`: For UUID primary keys.
- `pydantic.BaseModel`, `Field`: For schema and validation.
- `os`, `logging`, `datetime`, `uuid`, `random`, `decimal`, `typing` (standard library utilities).

### Custom Functions/Utilities
- `get_db`: Yields an async DB session for dependency injection.
- `create_tables`: Creates DB tables if not present.
- `populate_sample_inventory`: Fills the inventory with sample data.
- `get_inventory_by_hotel`, `adjust_inventory`, `get_hotel_name_by_id`: Inventory service logic.

This section provides a reference for all endpoints, libraries, and core FastAPI features used in this microservice project, supporting both learning and future development.

privacvy in logging: PII Filtering: The guest_name field is masked as [REDACTED] in all logs, and a utility is in place to mask this field in any dictionary logged.

## Scheduled Task: Automatic Room Return After Checkout

A new feature has been added to the booking service using APScheduler:

- **Daily Job:** APScheduler runs a background job every day when the FastAPI app is running.
- **Booking Check:** The job finds all bookings where the check-out date is in the past and the reservation status is still 'confirmed'.
- **Inventory Update:** For each such booking, the system automatically returns the room to inventory by incrementing `available_rooms` by 1 for the corresponding hotel and room type.
- **Booking Status Update:** The booking's reservation status is updated to 'completed'.

This automation ensures that rooms are returned to inventory after guests check out, keeping the inventory accurate without manual intervention.

# Dashboard Improvements Log

## Latest Updates

### 1. Standardized Color Scheme
- All panels now use a consistent color palette (green/yellow/orange/red/blue) for clarity and quick interpretation.

### 2. Endpoint Filtering
- Visualizations are now filtered to only show key API endpoints for Booking and Inventory services, reducing clutter from dynamic paths and payloads.
- PromQL regex is used to include only the desired endpoints in metrics panels.

### 3. 24h Time Range
- Key panels (requests, errors, booking failure ratio, etc.) are set to always display data from the last 24 hours using `"timeFrom": "24h"`.
- Panel titles are now clean and do not repeat the time range.

### 4. Auto-Refresh
- Dashboard refresh interval is set to 10 seconds for near real-time updates.
- Panels auto-refresh and do not require manual query execution.

### 5. Separate Loki Log Panels
- Two dedicated log panels have been added:
  - **Booking Service Logs**: Shows logs for the booking-service only.
  - **Inventory Service Logs**: Shows logs for the inventory-service only.
- Each panel uses the Loki data source and is customized for service-specific log queries.

---

**Benefits:**
- Cleaner, more actionable observability for both services.
- Easier troubleshooting with service-specific logs and metrics.
- Consistent, professional dashboard appearance.
- No more manual query refreshes needed.

---

*Last updated: 2025-06-27*

# 7. Security Best Practices: Secret Management in Microservices

A critical lesson in building production-grade microservices is the secure management of secrets and sensitive configuration values (such as `DATABASE_URL`).

- **Never commit secrets or sensitive values to version control.**
- For production, always use Kubernetes secrets, Helm secrets, or an external secrets manager (e.g., AWS KMS/Secrets Manager) to inject sensitive values.
- For local development, use a `.env` file (which is gitignored) or pass values via `--set` on the Helm CLI.
- Reference secrets in your `values.yaml` only as comments/examples, never with real values.

Example for production:
```yaml
# env:
#   DATABASE_URL: "your_real_db_url"
#   # Or, for Kubernetes Secret reference:
#   # DATABASE_URL:
#   #   valueFrom:
#   #     secretKeyRef:
#   #       name: my-db-url-secret
#   #       key: DATABASE_URL
```
Example for local development:
```bash
helm install my-release . \
  --set env.DATABASE_URL="your_real_db_url"
```

See the updated README for more details and patterns.

# CI/CD Pipeline & Code Quality Update (2024-06)

## GitHub Actions Matrix CI
- A new GitHub Actions workflow runs on every push and pull request to `main`.
- Uses a matrix build to independently test and lint both `booking_service` and `inventory_service`.
- Each service is set up in its own working directory, with dependencies installed via UV, linted with Ruff, and tested with pytest.
- This ensures both services are always validated in isolation, preventing cross-service issues.

## SonarCloud Integration
- SonarCloud is now integrated for automated code quality analysis, bug detection, and vulnerability scanning.
- Every commit and PR is analyzed, and results are visible on the [SonarCloud dashboard](https://sonarcloud.io/project/overview?id=crypticseeds_Hotel-Inventory-Booking-System).

---

# 8. GitOps with ArgoCD: Automated Kubernetes Deployments

A recent enhancement to the project is the adoption of [ArgoCD](https://argo-cd.readthedocs.io/) for GitOps-based Kubernetes deployments. All ArgoCD manifests are organized in the `argocd/` directory at the project root.

## Structure and Usage
- `argocd/project.yaml`: Defines an AppProject to group and manage both the booking and inventory services.
- `argocd/app-inventory.yaml` and `argocd/app-booking.yaml`: Application manifests for each service, referencing their respective Helm charts or manifests.

### Deployment Workflow
1. Apply the AppProject manifest:
   ```sh
   kubectl apply -f argocd/project.yaml
   ```
2. Apply the Application manifests:
   ```sh
   kubectl apply -f argocd/app-inventory.yaml
   kubectl apply -f argocd/app-booking.yaml
   ```
3. Use the ArgoCD UI or CLI to sync and monitor deployments.

## Benefits
- **Declarative Deployments:** All deployment configuration is version-controlled and auditable.
- **Unified Management:** Both services are managed together under a single project.
- **Easy Rollbacks:** Changes can be reverted by rolling back Git commits.
- **Visibility:** The ArgoCD UI provides real-time status and health of all managed applications.

This approach fits seamlessly into the microservices architecture, ensuring reliable, automated, and observable deployments for both the booking and inventory services.

---
