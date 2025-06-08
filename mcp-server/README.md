# Database MCP Server

A Model Context Protocol (MCP) server that provides access to multiple database types including PostgreSQL, Redis, MongoDB, and InfluxDB.

## Features

- Support for PostgreSQL, Redis, MongoDB, and InfluxDB
- Toggle individual databases on/off via environment variables
- Dual mode operation: STDIO for MCP Inspector and HTTP for production
- Docker support for easy deployment
- Automated CI/CD with Drone

## Development

### MCP Inspector Mode (Default)
```bash
# Run with MCP Inspector
python main.py

# Or explicitly specify stdio mode
python main.py --mode stdio
```

### HTTP Mode for Testing
```bash
# Run HTTP server for testing
python main.py --mode http --host localhost --port 8000
```

## Production Deployment

### Docker Build
```bash
# Build the Docker image
docker build -t mcp-server .

# Run with environment variables
docker run -p 8000:8000 \
  -e POSTGRES_HOST=your-db-host \
  -e POSTGRES_PASSWORD=your-password \
  -e INFLUXDB_TOKEN=your-token \
  mcp-server
```

### Environment Variables
Copy `.env.example` to `.env` and configure your database connections:

```bash
# Enable/disable databases
ENABLE_POSTGRES=true
ENABLE_REDIS=true
ENABLE_MONGODB=true
ENABLE_INFLUXDB=true

# Database connection details
POSTGRES_HOST=localhost
POSTGRES_PASSWORD=your_password
INFLUXDB_TOKEN=your_token
# ... see .env.example for all options
```

### Docker Registry
The CI/CD pipeline automatically builds and publishes to `repo.wheeler-network.com/mcp-server`.

## Usage

Once running, the server provides MCP tools for:
- PostgreSQL: Query execution, schema inspection, data manipulation
- Redis: Key-value operations, pub/sub, data structure operations
- MongoDB: Document operations, collection management, aggregation
- InfluxDB: Time-series data queries, bucket management, measurements

## API Modes

- **STDIO Mode**: For MCP Inspector and direct MCP client connections
- **HTTP Mode**: RESTful API for production deployments with uvicorn

The server automatically configures logging appropriately for each mode.