# Helm Charts for Hotel Inventory Booking System

This directory contains independent Helm charts for each microservice:

- `booking_service`: Handles booking operations.
- `inventory_service`: Manages inventory data.

## Deploying a Service

To deploy a service (example for inventory):

```bash
cd Helm/inventory_service
helm install inventory-service .
```

## Why this structure?

Each service is packaged as its own Helm chart for independent deployment and management, reflecting best practices for scalable microservice architectures.