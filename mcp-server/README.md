# Database MCP Server

A Model Context Protocol (MCP) server that provides access to multiple database types including PostgreSQL, Redis, MongoDB, and InfluxDB.

## Features

- Support for PostgreSQL, Redis, MongoDB, and InfluxDB
- Toggle individual databases on/off via environment variables
- Dual mode operation: STDIO for MCP Inspector and HTTP for production
- Docker support for easy deployment
- Automated CI/CD with GitHub Actions
- Comprehensive environment variable configuration
- Multi-platform Docker builds (linux/amd64, linux/arm64)

## Development

### HTTP Mode for Testing
```bash
# Run HTTP server for testing
python main.py --mode http

npx @modelcontextprotocol/inspector
```

## Production Deployment

### Docker Build
```bash
# Build the Docker image
docker build -t mcp-server .

# Pull from registry
docker pull repo.wheeler-network.com/mcp-server:latest
```

### Complete Docker Run Command
```bash
# Run with all available environment variables
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e ENABLE_POSTGRES=true \
  -e ENABLE_REDIS=true \
  -e ENABLE_MONGODB=true \
  -e ENABLE_INFLUXDB=true \
  -e POSTGRES_HOST=your-postgres-host \
  -e POSTGRES_PORT=5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your-postgres-password \
  -e POSTGRES_DB=your-database \
  -e REDIS_HOST=your-redis-host \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD=your-redis-password \
  -e REDIS_DB=0 \
  -e MONGODB_HOST=your-mongodb-host \
  -e MONGODB_PORT=27017 \
  -e MONGODB_USER=your-mongodb-user \
  -e MONGODB_PASSWORD=your-mongodb-password \
  -e MONGODB_DB=your-mongodb-database \
  -e INFLUXDB_HOST=your-influxdb-host \
  -e INFLUXDB_PORT=8086 \
  -e INFLUXDB_TOKEN=your-influxdb-token \
  -e INFLUXDB_ORG=your-influxdb-org \
  -e INFLUXDB_BUCKET=your-influxdb-bucket \
  repo.wheeler-network.com/mcp-server:latest
```

### Minimal Docker Run (PostgreSQL only)
```bash
# Run with only PostgreSQL enabled
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -e ENABLE_POSTGRES=true \
  -e ENABLE_REDIS=false \
  -e ENABLE_MONGODB=false \
  -e ENABLE_INFLUXDB=false \
  -e POSTGRES_HOST=your-postgres-host \
  -e POSTGRES_PASSWORD=your-postgres-password \
  repo.wheeler-network.com/mcp-server:latest
```

### Custom Port for Reverse Proxy
```bash
# Run on custom port for reverse proxy setup (e.g., mcp.wheeler-network.com)
docker run -d \
  --name mcp-server \
  -p 3000:3000 \
  -e HOST=0.0.0.0 \
  -e PORT=3000 \
  -e POSTGRES_HOST=your-postgres-host \
  -e POSTGRES_PASSWORD=your-postgres-password \
  repo.wheeler-network.com/mcp-server:latest
```

### Environment Variables
All environment variables with their defaults:

#### Server Configuration
```bash
HOST=0.0.0.0                    # Host to bind to
PORT=8000                       # Port to expose the service on
```

#### Database Toggles
```bash
ENABLE_POSTGRES=true            # Enable/disable PostgreSQL support
ENABLE_REDIS=true               # Enable/disable Redis support
ENABLE_MONGODB=true             # Enable/disable MongoDB support
ENABLE_INFLUXDB=true            # Enable/disable InfluxDB support
```

#### PostgreSQL Configuration
```bash
POSTGRES_HOST=postgres          # PostgreSQL host
POSTGRES_PORT=5432              # PostgreSQL port
POSTGRES_USER=postgres          # PostgreSQL username
POSTGRES_PASSWORD=""            # PostgreSQL password (required)
POSTGRES_DB=""                  # Optional: specific database name
```

#### Redis Configuration
```bash
REDIS_HOST=redis                # Redis host
REDIS_PORT=6379                 # Redis port
REDIS_PASSWORD=""               # Redis password (optional)
REDIS_DB=0                      # Redis database number
```

#### MongoDB Configuration
```bash
MONGODB_HOST=mongodb            # MongoDB host
MONGODB_PORT=27017              # MongoDB port
MONGODB_USER=""                 # MongoDB username (optional)
MONGODB_PASSWORD=""             # MongoDB password (optional)
MONGODB_DB=""                   # MongoDB database name (optional)
```

#### InfluxDB Configuration
```bash
INFLUXDB_HOST=influxdb          # InfluxDB host
INFLUXDB_PORT=8086              # InfluxDB port
INFLUXDB_TOKEN=""               # InfluxDB authentication token (required)
INFLUXDB_ORG=""                 # InfluxDB organization (required)
INFLUXDB_BUCKET=""              # InfluxDB bucket name (required)
```

**Note**: Copy `.env.example` to `.env` and configure your database connections for local development.

### CI/CD Pipeline
The GitHub Actions pipeline automatically:
1. **Lints** code with `ruff` for formatting and style checks
2. **Security scans** with `bandit` and `safety` for vulnerabilities
3. **Builds** multi-platform Docker images (linux/amd64, linux/arm64)
4. **Publishes** to `repo.wheeler-network.com/mcp-server` with tags:
   - `latest` (on main/master branch)
   - `{branch}-{commit-sha}` (commit-specific tags)

### Repository Secrets Required
Configure these secrets in your GitHub repository settings:
- `REPO_USER`: Docker registry username
- `REPO_PASS`: Docker registry password

## Usage

Once running, the server provides MCP tools for:
- PostgreSQL: Query execution, schema inspection, data manipulation
- Redis: Key-value operations, pub/sub, data structure operations
- MongoDB: Document operations, collection management, aggregation
- InfluxDB: Time-series data queries, bucket management, measurements

## API Modes

- **STDIO Mode**: For MCP Inspector and direct MCP client connections
- **HTTP Mode**: RESTful API for production deployments with uvicorn

The server automatically configures logging appropriately for each mode (stderr for STDIO, normal logging for HTTP).

## Architecture

The server is organized into modular database-specific packages:
- `postgres_db/` - PostgreSQL tools, resources, and connection management
- `redis_db/` - Redis operations and data structure tools
- `mongodb_db/` - MongoDB document operations and collection management
- `influxdb_db/` - InfluxDB time-series data queries and bucket operations

Each database module can be independently enabled/disabled via environment variables.