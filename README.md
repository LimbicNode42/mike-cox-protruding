# Database MCP Server

A comprehensive database management MCP (Model Context Protocol) server supporting multiple database types with TypeScript implementation following MC-PEA standards.

## 🚀 Features

### Supported Databases
- **PostgreSQL** - Relational database operations (queries, commands, schema management)
- **Redis** - Key-value store operations (get, set, delete, flush)
- **MongoDB** - Document database operations (find, insert, update, delete)
- **InfluxDB** - Time-series database operations (query, write, bucket management)

### MCP Protocol Compliance
- ✅ Uses MCP SDK stdio transport for VS Code integration
- ✅ Proper tool registration with `server.registerTool()`
- ✅ Session-based database connection management
- ✅ Zod schema validation for all tool inputs
- ✅ Comprehensive error handling and logging

## 📋 Prerequisites

- Node.js 18+ and npm
- TypeScript 5.4+
- Access to database servers (PostgreSQL, Redis, MongoDB, InfluxDB as needed)

## 🛠️ Installation

1. **Clone or navigate to the project**:
   ```bash
   cd mcp-servers/db-mcp-server
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your database configurations
   ```

4. **Build the project**:
   ```bash
   npm run build
   ```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
API_KEY=your-secret-api-key-here

# PostgreSQL (enabled by default)
ENABLE_POSTGRES=true
POSTGRES_URL=postgresql://username:password@localhost:5432/database

# Redis (disabled by default)
ENABLE_REDIS=false
REDIS_URL=redis://localhost:6379

# MongoDB (disabled by default)  
ENABLE_MONGODB=false
MONGODB_URL=mongodb://localhost:27017/database

# InfluxDB (disabled by default)
ENABLE_INFLUXDB=false
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-influxdb-token
INFLUXDB_ORG=your-org
INFLUXDB_BUCKET=your-bucket

# Server Configuration
NODE_ENV=development
PORT=3001
```

### Database-Specific Configuration

#### PostgreSQL
- **Required**: `POSTGRES_URL` - Full PostgreSQL connection string
- **Format**: `postgresql://user:password@host:port/database`

#### Redis
- **Required**: `REDIS_URL` - Redis connection string
- **Format**: `redis://host:port` or `redis://user:password@host:port`

#### MongoDB
- **Required**: `MONGODB_URL` - MongoDB connection string
- **Format**: `mongodb://user:password@host:port/database`

#### InfluxDB
- **Required**: `INFLUXDB_URL`, `INFLUXDB_TOKEN`
- **Optional**: `INFLUXDB_ORG`, `INFLUXDB_BUCKET` (defaults can be set)

## 🚀 Usage

### As MCP Server (VS Code Integration)

1. **Start the server**:
   ```bash
   npm start
   # or for development
   npm run dev
   ```

2. **Configure in VS Code**:
   Add to your VS Code MCP configuration:
   ```json
   {
     "mcpServers": {
       "db-mcp-server": {
         "command": "node",
         "args": ["path/to/db-mcp-server/dist/index.js", "--stdio"],
         "env": {
           "API_KEY": "your-api-key"
         }
       }
     }
   }
   ```

### Available Tools

#### PostgreSQL Tools
- `postgres_query` - Execute SELECT queries
- `postgres_execute` - Execute SQL statements (INSERT, UPDATE, DELETE, etc.)
- `postgres_create_table` - Create new tables
- `postgres_create_database` - Create new databases

#### Redis Tools
- `redis_get` - Get value by key
- `redis_set` - Set value with optional expiration
- `redis_delete` - Delete one or more keys
- `redis_flush` - Clear database

#### MongoDB Tools
- `mongo_find` - Find documents in collections
- `mongo_insert` - Insert documents
- `mongo_update` - Update documents
- `mongo_delete` - Delete documents

#### InfluxDB Tools
- `influx_query` - Execute Flux queries
- `influx_write` - Write data points
- `influx_buckets` - List available buckets

## 🧪 Testing

### Run Tests
```bash
# All tests
npm test

# Unit tests only
npm run test:unit

# Integration tests only
npm run test:integration

# MCP client validation
npm run test:mcp
```

### Validate Implementation
```bash
# Validate against MC-PEA template
npm run validate
```

## 🔧 Development

### Project Structure
```
src/
├── index.ts              # Main server entry point
├── registrations.ts      # Tool and resource registration
├── types/
│   └── session.ts        # Session and configuration types
└── tools/
    ├── postgres.ts       # PostgreSQL tools
    ├── redis.ts          # Redis tools
    ├── mongodb.ts        # MongoDB tools
    └── influxdb.ts       # InfluxDB tools
```

### Development Commands
```bash
# Development with auto-reload
npm run dev

# Build TypeScript
npm run build

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
```

## 🔒 Security

### Authentication
- API key authentication required for all operations
- Session-based database connection management
- Input validation using Zod schemas

### Best Practices
- Never commit `.env` files with real credentials
- Use strong API keys in production
- Configure database access controls appropriately
- Enable SSL/TLS for database connections in production

## 🐛 Troubleshooting

### Common Issues

1. **Connection Errors**:
   - Verify database servers are running
   - Check connection strings in `.env`
   - Ensure network connectivity

2. **Permission Errors**:
   - Verify database user permissions
   - Check authentication credentials

3. **MCP Integration Issues**:
   - Ensure API_KEY is correctly configured
   - Verify stdio transport is working
   - Check VS Code MCP configuration

### Debug Mode
```bash
# Enable debug logging
LOG_LEVEL=debug npm run dev
```

## 📚 Documentation

- [MC-PEA Master Reference](../../MCP_MASTER_REFERENCE.md)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [TypeScript SDK Documentation](https://github.com/modelcontextprotocol/typescript-sdk)

## 🤝 Contributing

1. Follow MC-PEA development standards
2. Ensure all tests pass
3. Update documentation for new features
4. Use proper TypeScript types
5. Follow the established tool registration patterns

## 📄 License

Part of the MC-PEA project. See project root for license information.

## 🆔 Version

**Version**: 1.0.0  
**Compatibility**: MC-PEA Template v1.0+  
**MCP SDK**: Compatible with @modelcontextprotocol/sdk v1.0+