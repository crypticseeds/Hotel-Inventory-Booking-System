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
