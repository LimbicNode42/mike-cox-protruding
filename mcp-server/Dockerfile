# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install UV package manager
RUN pip install uv

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY . .

# Environment variables for server configuration
ENV HOST=0.0.0.0

# Environment variables for database toggles
ENV ENABLE_POSTGRES=true
ENV ENABLE_REDIS=true
ENV ENABLE_MONGODB=true
ENV ENABLE_INFLUXDB=true

# PostgreSQL configuration
ENV POSTGRES_HOST=postgres
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=""
ENV POSTGRES_DB=""

# Redis configuration
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=""
ENV REDIS_DB=0

# MongoDB configuration
ENV MONGODB_HOST=mongodb
ENV MONGODB_PORT=27017
ENV MONGODB_USER=""
ENV MONGODB_PASSWORD=""
ENV MONGODB_DB=""

# InfluxDB configuration
ENV INFLUXDB_HOST=influxdb
ENV INFLUXDB_PORT=8086
ENV INFLUXDB_TOKEN=""
ENV INFLUXDB_ORG=""
ENV INFLUXDB_BUCKET=""

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["sh", "-c", "uv run python main.py --mode http --host $HOST --port 8000"]
