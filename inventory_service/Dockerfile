# syntax=docker/dockerfile:1

FROM python:3.13.5-slim AS base

# Use a separate stage to get the uv binary
FROM ghcr.io/astral-sh/uv:latest AS uv-builder

FROM base AS final

# Copy uv from builder
COPY --from=uv-builder /uv /uvx /bin/

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Copy only necessary files
WORKDIR /app

# Copy only dependency files first for better caching
COPY pyproject.toml ./

# Install dependencies using uv (from pyproject.toml)
RUN if [ -f uv.lock ]; then uv pip install --system -r uv.lock; else uv pip install --system -r pyproject.toml; fi

# Copy the rest of the application code
COPY app ./app

# Install the project in editable mode
RUN uv pip install --system -e .

# Change to non-root user
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 
