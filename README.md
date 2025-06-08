# MCP Database Server

A production-ready Model Context Protocol (MCP) server providing database connectivity and management tools for PostgreSQL, Redis, MongoDB, and InfluxDB. Built with modular architecture supporting selective database activation via environment variables.

## 🚀 Features

- **Multi-Database Support**: PostgreSQL, Redis, MongoDB, InfluxDB
- **Modular Architecture**: Enable/disable databases independently
- **Production Ready**: Docker containerization with reverse proxy
- **Comprehensive Testing**: Unit, integration, and load tests
- **CI/CD Pipeline**: Automated testing and deployment with DroneCI
- **Security Hardened**: Non-root containers, security headers, rate limiting
- **Health Monitoring**: Built-in health checks and observability
- **Development Tools**: Makefile automation for common tasks

## 📋 Prerequisites

- Python 3.11+
- Docker and Docker Compose
- uv (Python package manager)
- Make (optional, for automation)

## 🏃 Quick Start

### Development Setup

1. **Clone and Setup**
   ```bash
   cd mcp-server
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install uv
   uv pip install -e .
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database configurations
   ```

3. **Start Development Server**
   ```bash
   # MCP development server (stdio transport)
   mcp dev main.py
   
   # HTTP server for production testing
   python server.py
   ```

### Docker Production Setup

1. **Start Full Stack**
   ```bash
   # Start all services
   make up
   
   # Or manually
   docker-compose up -d
   ```

2. **Check Service Health**
   ```bash
   make health
   
   # Or manually check
   curl http://localhost/health
   ```

3. **View Logs**
   ```bash
   make logs
   
   # Or specific service
   docker-compose logs -f mcp-server
   ```

## 🗂️ Project Structure

```
mcp-server/
├── config.py              # Configuration management
├── main.py                # MCP development server (stdio)
├── server.py              # HTTP production server
├── tools.py               # MCP tools registration
├── docker/                # Docker configurations
│   ├── nginx/             # Reverse proxy config
│   ├── postgres/          # PostgreSQL init scripts
│   └── mongodb/           # MongoDB init scripts
├── postgres_db/           # PostgreSQL tools and resources
├── redis_db/              # Redis tools and resources
├── mongodb_db/            # MongoDB tools and resources
├── influxdb_db/           # InfluxDB tools and resources
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── load/              # Load testing scripts
├── docker-compose.yml     # Production services
├── docker-compose.test.yml # Test environment
├── Dockerfile             # Production image
├── Dockerfile.test        # Test image
├── Makefile              # Development automation
└── .drone.yml            # CI/CD pipeline
```

## ⚙️ Configuration

### Environment Variables

The server can be configured via environment variables or `.env` file:

#### Server Configuration
```bash
SERVER_HOST=localhost          # Server bind address
SERVER_PORT=8000              # Server port
CORS_ORIGINS=*                # CORS allowed origins (comma-separated)
```

#### Database Toggles
```bash
ENABLE_POSTGRES=true          # Enable PostgreSQL support
ENABLE_REDIS=true             # Enable Redis support
ENABLE_MONGODB=true           # Enable MongoDB support
ENABLE_INFLUXDB=true          # Enable InfluxDB support
```

#### Database Connections
```bash
# PostgreSQL
POSTGRES_URL=postgresql://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# MongoDB
MONGODB_URL=mongodb://localhost:27017/database

# InfluxDB
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-token
INFLUXDB_ORG=your-org
INFLUXDB_BUCKET=your-bucket
```

### Selective Database Activation

Enable only the databases you need:

```bash
# Only PostgreSQL and Redis
ENABLE_POSTGRES=true
ENABLE_REDIS=true
ENABLE_MONGODB=false
ENABLE_INFLUXDB=false
```

Disabled databases:
- Won't be initialized or connected to
- Their tools will return helpful error messages
- Reduce resource usage and startup time

## 🔧 Development

### Available Make Commands

```bash
# Development
make install          # Install dependencies
make dev             # Start development server
make server          # Start HTTP server

# Docker Operations
make build           # Build all images
make up              # Start all services
make down            # Stop all services
make restart         # Restart services
make logs            # View logs

# Testing
make test            # Run all tests
make test-unit       # Run unit tests only
make test-integration # Run integration tests
make test-load       # Run load tests

# Code Quality
make lint            # Run linting
make lint-fix        # Fix code formatting
make type-check      # Run type checking
make security-scan   # Run security scans

# Database Operations
make db-init         # Initialize databases
make db-backup       # Backup databases
make db-restore      # Restore databases

# Monitoring
make health          # Check service health
make stats           # View resource usage
make monitor         # Start monitoring dashboard

# Cleanup
make clean           # Clean up containers and volumes
make prune           # Clean Docker system
```

### Running Tests

```bash
# All tests
make test

# Specific test categories
pytest tests/unit/                    # Unit tests
pytest tests/integration/ -m integration # Integration tests
pytest tests/integration/ -m performance # Performance tests

# With coverage
pytest --cov=. --cov-report=html tests/

# Specific test file
pytest tests/unit/test_config.py -v
```

### Load Testing

```bash
# Basic load test
make test-load

# Custom k6 tests
docker-compose -f docker-compose.test.yml up load-tester

# Manual k6 testing
k6 run --env MCP_SERVER_URL=http://localhost:8000 tests/load/load-test.js
```

## 🐳 Docker Deployment

### Production Deployment

1. **Environment Setup**
   ```bash
   cp .env.production .env
   # Configure production settings
   ```

2. **Deploy Services**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **SSL/TLS Setup** (Optional)
   ```bash
   # Add SSL certificates to docker/nginx/ssl/
   # Update nginx configuration for HTTPS
   ```

### Service Architecture

- **Nginx**: Reverse proxy with rate limiting and SSL termination
- **MCP Server**: Main application server
- **PostgreSQL**: Relational database with initialization scripts
- **Redis**: In-memory cache and session store
- **MongoDB**: Document database with sample collections
- **InfluxDB**: Time-series database for metrics

### Health Checks

All services include health checks:
- **HTTP endpoints**: `/health` for application status
- **Database connections**: Automatic retry with exponential backoff
- **Service dependencies**: Proper startup ordering

## 🧪 Testing Strategy

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Configuration parsing
   - Server creation and routing
   - Tool registration logic
   - Mock database managers

2. **Integration Tests** (`tests/integration/`)
   - Real database connections
   - End-to-end MCP workflows
   - Service interaction testing
   - Performance benchmarks

3. **Load Tests** (`tests/load/`)
   - k6 performance testing
   - Concurrent request handling
   - Stress testing scenarios
   - Resource usage monitoring

### Test Execution

```bash
# Local testing
make test

# Docker testing (isolated environment)
docker-compose -f docker-compose.test.yml up --build test-runner

# CI/CD testing (automated)
# Tests run automatically on git push via DroneCI
```

## 🚀 CI/CD Pipeline

The project includes a comprehensive DroneCI pipeline:

### Pipeline Stages

1. **Code Quality**
   - Linting (black, isort, flake8)
   - Type checking (mypy)
   - Security scanning (bandit, safety)

2. **Testing**
   - Unit tests with coverage
   - Integration tests with real databases
   - Load testing with k6

3. **Build & Deploy**
   - Docker image building
   - Multi-architecture support
   - Staging deployment
   - Production deployment (on main branch)

4. **Notifications**
   - Slack notifications for build status
   - Email alerts for failures

### Deployment Environments

- **Development**: Local development with hot reload
- **Staging**: Temporary environment for testing
- **Production**: Full production deployment with monitoring

## 📊 Monitoring & Observability

### Built-in Monitoring

- **Health Endpoints**: `/health` for service status
- **Metrics Collection**: Request timing and error rates
- **Structured Logging**: JSON logs with correlation IDs
- **Resource Monitoring**: Memory and CPU usage tracking

### Production Monitoring

Add these services for comprehensive monitoring:

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus:latest
  # Configuration...

grafana:
  image: grafana/grafana:latest
  # Configuration...

loki:
  image: grafana/loki:latest
  # Configuration...
```

## 🔒 Security

### Security Features

- **Container Security**: Non-root user, minimal attack surface
- **Network Security**: Service isolation, firewall rules
- **HTTP Security**: Security headers, CORS protection
- **Rate Limiting**: Request throttling and DDoS protection
- **Input Validation**: Parameter sanitization and validation

### Security Best Practices

1. **Secrets Management**
   - Use environment variables for sensitive data
   - Never commit secrets to git
   - Rotate credentials regularly

2. **Network Security**
   - Use internal Docker networks
   - Expose only necessary ports
   - Enable firewall rules

3. **Application Security**
   - Regular dependency updates
   - Security scanning in CI/CD
   - Input validation and sanitization

## 🤝 Contributing

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/mcp-server.git
   cd mcp-server
   ```

2. **Setup Development Environment**
   ```bash
   make install
   make dev
   ```

3. **Make Changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

4. **Test Your Changes**
   ```bash
   make test
   make lint
   make type-check
   ```

5. **Submit Pull Request**
   - Clear description of changes
   - Reference any related issues
   - Include test results

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Failures**
   ```bash
   # Check service status
   docker-compose ps
   
   # View service logs
   docker-compose logs postgres
   
   # Test connectivity
   make health
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Use different ports
   SERVER_PORT=8001 python server.py
   ```

3. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   
   # Docker permission issues
   sudo usermod -aG docker $USER
   ```

4. **Memory Issues**
   ```bash
   # Monitor resource usage
   make stats
   
   # Adjust Docker limits
   docker-compose down
   # Edit docker-compose.yml memory limits
   docker-compose up -d
   ```

### Getting Help

- **Documentation**: Check this README and inline code comments
- **Issues**: Open a GitHub issue with detailed error information
- **Logs**: Include relevant logs when reporting issues
- **Configuration**: Share your (sanitized) configuration when asking for help

---

**Happy coding! 🎉**