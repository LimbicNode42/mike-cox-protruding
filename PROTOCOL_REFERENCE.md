# Database MCP Server - Protocol Reference

This document provides detailed information about the Model Context Protocol (MCP) implementation for the Database MCP Server.

## Protocol Overview

The Database MCP Server implements the Model Context Protocol to provide secure, structured access to multiple database systems including:

- **PostgreSQL** - Relational database queries and operations
- **Redis** - Key-value store operations
- **MongoDB** - Document database operations  
- **InfluxDB** - Time series data operations

## Server Information

- **Name**: `db-mcp-server`
- **Version**: `1.0.0`
- **Protocol Version**: MCP 1.0

## Transport Support

### Supported Transports

1. **Standard I/O (stdio)** - For VS Code integration and local development
   - Default transport for editor integrations
   - Bidirectional communication over stdin/stdout

2. **HTTP (planned)** - For web applications and remote access
   - RESTful API endpoints
   - Session management
   - Authentication via API keys

### Connection Example

```bash
# Start server in stdio mode (default)
node dist/index.js --stdio

# HTTP mode (planned)
node dist/index.js --http --port 3001
```

## Tools

The server provides database-specific tools for each supported database type.

### PostgreSQL Tools

#### `postgres_query`
Execute SQL queries against PostgreSQL databases.

**Input Schema:**
```json
{
  "type": "object", 
  "properties": {
    "query": {
      "type": "string",
      "description": "SQL query to execute"
    }
  },
  "required": ["query"]
}
```

**Example:**
```json
{
  "query": "SELECT * FROM users LIMIT 10"
}
```

### Redis Tools

#### `redis_get`
Retrieve values from Redis by key.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "key": {
      "type": "string", 
      "description": "Redis key to get"
    }
  },
  "required": ["key"]
}
```

### MongoDB Tools

#### `mongodb_find`
Find documents in MongoDB collections.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "database": {
      "type": "string",
      "description": "Database name" 
    },
    "collection": {
      "type": "string",
      "description": "Collection name"
    },
    "query": {
      "type": "object",
      "description": "Query filter (optional)"
    }
  },
  "required": ["database", "collection"]
}
```

### InfluxDB Tools

#### `influxdb_query`
Execute Flux queries against InfluxDB.

**Input Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Flux query to execute"
    }
  },
  "required": ["query"]
}
```

## Resources (Planned)

Future implementation will include read-only resources for:

- Database schema information
- Connection status and health checks
- Performance metrics
- Available databases and collections

## Error Handling

All tools return structured responses with error information:

```json
{
  "success": false,
  "error": "Error message here",
  "code": "ERROR_CODE"
}
```

## Security

- Environment-based configuration
- Optional API key authentication
- Connection pooling and cleanup
- Input validation and sanitization

## Configuration

See `.env.example` for all available configuration options.
