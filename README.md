# Hotel Inventory and Booking System

This project is a microservices-based application for managing hotel inventory and bookings. It's designed to be scalable and maintainable, with a clear separation of concerns between services.

## Tools Used
- FastAPI
- Sentry
- PostgreSQL (Neon Postgres)
- Uvicorn
- Docker & Docker Compose
- OpenTelemetry
- Loki
- Prometheus
- Grafana
- Sonarcloud
- Github Actions
- Linkered

## Project Architecture

The application is composed of three main components:

-   `gateway/`: An API Gateway that acts as a single entry point for all incoming requests and routes them to the appropriate backend service.
-   `inventory_service/`: Manages hotel room availability, pricing, and hotel information.
-   `booking_service/`: Handles the creation and management of customer bookings.

Each service is a standalone FastAPI application, containerized with Docker.

## Database

Both services use PostgreSQL as the database, with schemas defined using SQLAlchemy ORM. See the service-specific READMEs for schema details.

## Dependency Management Policy: Use UV

All Python dependency management, including environment setup and Docker builds, **must use [UV](https://docs.astral.sh/uv)**.

- Install dependencies:
  ```bash
  uv pip install -e .
  ```

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

- **API Gateway**: 
  - Production/Cloud: AWS API Gateway (URL provided by your AWS deployment)
  - Local Development: `http://localhost:8080`
- **Booking Service**: `http://localhost:8002`
- **Inventory Service**: `http://localhost:8001`

## Running Services for Development

To run a service directly (without Docker), navigate to the respective `app` directory and run:

**Booking Service:**
```bash
cd booking_service/app
uvicorn main:app --reload --host 0.0.0.0 --port 8002
```

**Inventory Service:**
```bash
cd inventory_service/app
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Make sure you have all dependencies installed using `uv` as described above.

## Monitoring & Observability

The system includes observability and monitoring features:
- **OpenTelemetry** for distributed tracing
- **Prometheus** for metrics collection
- **Loki** for log aggregation
- **Grafana** for dashboards

To access Grafana dashboards, visit: `http://localhost:3000` (default credentials: `admin`/`admin`)

See `otel-collector-config.yaml` and `otel-dashboard.json` for configuration and dashboard setup.

## Service Details

For detailed information about each service, including API endpoints, database schema, and service-specific logic, please refer to the respective README files:
- [Booking Service](./booking_service/README.md)
- [Inventory Service](./inventory_service/README.md)

## CI/CD & Code Quality

This project uses GitHub Actions for continuous integration (CI) and SonarCloud for code quality analysis:

- **GitHub Actions CI:**
  - On every push and pull request to `main`, a matrix build runs for both `booking_service` and `inventory_service`.
  - Each service is tested in isolation: dependencies are installed with [UV](https://docs.astral.sh/uv/), code is linted with Ruff, and tests are run with pytest.
  - The workflow file is located at `.github/workflows/ci.yml`.
- **SonarCloud:**
  - Code quality, bugs, and vulnerabilities are automatically analyzed for every commit and pull request.
  - See the live dashboard: [SonarCloud Project Overview](https://sonarcloud.io/project/overview?id=crypticseeds_Hotel-Inventory-Booking-System)

---


## Future Enhancements
- Enforce idempotency for POST /booking to avoid duplicates.
- Service-to-service communication via message broker (e.g., Kafka, EventBridge).

## Kubernetes Helm Charts

This project includes Helm charts for deploying the Booking and Inventory services to Kubernetes. The charts are located in the `Helm-charts/` directory:

- `Helm-charts/booking-service/`
- `Helm-charts/inventory-service/`

### Chart Features
- Minimal working Deployment and Service for each microservice
- Sensible defaults for image and ports (see `values.yaml` in each chart)
- Helm test hooks for basic connectivity testing
- Follows Kubernetes naming conventions (uses hyphens, not underscores)
- **Built-in support for Linkerd service mesh:**
  - Each service's deployment includes the annotation `linkerd.io/inject: "enabled"` by default (configurable via `values.yaml`).
  - This enables automatic Linkerd sidecar injection, providing secure, encrypted (mTLS) service-to-service communication, zero-trust networking, and detailed observability for all traffic between services.

### Usage

**Lint the charts:**
```bash
helm lint Helm-charts/booking-service
helm lint Helm-charts/inventory-service
```

**Dry-run install (shows rendered resources without deploying):**
```bash
helm install booking-test Helm-charts/booking-service --dry-run --debug
helm install inventory-test Helm-charts/inventory-service --dry-run --debug
```

**Install to your cluster:**
```bash
helm install booking-test Helm-charts/booking-service --set env.DATABASE_URL="your_real_db_url"
helm install inventory-test Helm-charts/inventory-service --set env.DATABASE_URL="your_real_db_url"
```


See the NOTES.txt in each chart for port-forwarding and access instructions after deployment.

## Security Best Practices: Secrets and Sensitive Values

**Never commit secrets or sensitive values (like DATABASE_URL) to version control.**

- For production, use Kubernetes secrets, Helm secrets, or an external secrets manager (e.g., AWS KMS/Secrets Manager) to inject sensitive values.
- For local development, use a `.env` file (which is gitignored) or pass values via `--set` on the Helm CLI.
- Reference secrets in your `values.yaml` only as comments/examples, never with real values.

Example for production:
```yaml
# env:
#   - name: DATABASE_URL
#     valueFrom:
#       secretKeyRef:
#         name: my-db-url-secret
#         key: DATABASE_URL
```
Example for local development:
```bash
helm install my-release . \
  --set env.DATABASE_URL="your_real_db_url"
```

**.env files and any secret YAMLs should always be in your .gitignore.**

---

For more information on contributing, troubleshooting, or advanced configuration, see the service-specific documentation.

## GitOps Deployment with ArgoCD

This project supports GitOps-style Kubernetes deployments using [ArgoCD](https://argo-cd.readthedocs.io/). All ArgoCD manifests are located in the `argocd/` directory at the project root.

### Directory Structure
- `argocd/project.yaml`: Defines an ArgoCD AppProject for unified management of both services.
- `argocd/app-inventory.yaml`: ArgoCD Application manifest for the Inventory Service.
- `argocd/app-booking.yaml`: ArgoCD Application manifest for the Booking Service.

### How to Use
1. **Apply the AppProject**
   ```sh
   kubectl apply -f argocd/project.yaml
   ```
2. **Apply the Application Manifests**
   ```sh
   kubectl apply -f argocd/app-inventory.yaml
   kubectl apply -f argocd/app-booking.yaml
   ```
3. **Sync and Monitor**
   - Use the ArgoCD UI or CLI to sync and monitor both applications. Both services will be launched and managed together under the defined project.

> **Note:**
> - Update the `repoURL` and `path` fields in the Application manifests to match your repository and deployment structure.
> - Ensure your Git repository is registered as a source in ArgoCD.

For more details, see `argocd/README.md`.
