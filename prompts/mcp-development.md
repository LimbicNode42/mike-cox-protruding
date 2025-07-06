# MCP Development Guidelines for Database MCP Server

## Overview
This document provides development guidelines specific to the Database MCP Server, ensuring consistency with MC-PEA project standards and MCP protocol compliance.

## Core Principles

### 1. MCP Protocol Compliance
- **ALWAYS use MCP SDK transports** - Never create custom HTTP servers outside of MCP
- **ALWAYS use `server.registerTool()` with proper patterns** - Follow the 3-argument signature
- **ALWAYS validate with MCP SDK client** - Test with actual MCP client connections
- **ALWAYS follow template patterns** - Use established MC-PEA patterns

### 2. Database-Specific Requirements
- Support multiple database types with unified interface
- Implement session-based connection management
- Provide consistent error handling across all databases
- Use environment-based configuration for security

### 3. Security Standards
- Never hardcode database credentials
- Use environment variables for all sensitive configuration
- Implement proper connection cleanup
- Validate all input parameters with Zod schemas

## Architecture Requirements

### Server Structure
```
src/
├── index.ts           # Main entry point, transport setup
├── registrations.ts   # Tool/resource registration hub
├── types/
│   └── session.ts     # Session and client management
├── tools/             # Database-specific tool implementations
└── resources/         # Database schema and metadata access
```

### Tool Implementation Pattern
```typescript
server.registerTool(
  'database_operation',
  {
    description: 'Clear description of what the tool does',
    inputSchema: {
      field: z.string().describe('Descriptive field documentation')
    }
  },
  async (args: InputType) => {
    try {
      const session = await getOrCreateSession(sessionId, config, sessions);
      const result = await session.clients.database.operation(args);
      
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ ...result, success: true }, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ 
            error: error instanceof Error ? error.message : 'Unknown error', 
            success: false 
          }, null, 2)
        }]
      };
    }
  }
);
```

## Database Integration Patterns

### Connection Management
- Use session-based connection pooling
- Initialize connections lazily on first use
- Implement graceful connection cleanup
- Handle connection failures with clear error messages

### Supported Databases
1. **PostgreSQL** - Primary relational database support
2. **Redis** - Key-value operations and caching
3. **MongoDB** - Document store operations
4. **InfluxDB** - Time series data management

### Configuration Pattern
```typescript
interface DatabaseConfig {
  postgres: { enabled: boolean; url?: string };
  redis?: { enabled: boolean; url?: string };
  mongodb?: { enabled: boolean; url?: string };
  influxdb?: { enabled: boolean; url?: string; token?: string; org?: string };
}
```

## Development Workflow

### 1. Setup
```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit configuration
# Set database URLs and credentials in .env
```

### 2. Development
```bash
# Build TypeScript
npm run build

# Run in development mode
npm run dev

# Test server functionality
npm run test:mcp
```

### 3. Testing
- Always test tool registration and basic functionality
- Validate error handling with invalid inputs
- Test database connection handling
- Verify session cleanup

### 4. Validation
```bash
# Run template validation
npm run validate

# Run simple validation
node validation/validate-simple.js

# Run bash validation
bash validation/validate-bash.sh
```

## Common Patterns

### Error Response Format
```json
{
  "error": "Descriptive error message",
  "success": false,
  "details": "Optional additional context"
}
```

### Success Response Format
```json
{
  "result": "Actual data returned",
  "success": true,
  "metadata": {
    "rowCount": 10,
    "executionTime": "50ms"
  }
}
```

### Environment Variables
```bash
# Core configuration
API_KEY=your-api-key-here
NODE_ENV=development

# Database connections
POSTGRES_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379
MONGODB_URL=mongodb://localhost:27017
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your-token
INFLUXDB_ORG=your-org
```

## Troubleshooting

### Common Issues
1. **Tool registration fails** - Check Zod schema syntax and registerTool arguments
2. **Database connection errors** - Verify URLs and credentials in .env
3. **Session cleanup issues** - Ensure proper async/await in cleanup methods
4. **MCP client connection fails** - Check transport configuration and server startup

### Debugging Steps
1. Check server logs for error messages
2. Verify environment variable configuration
3. Test database connections independently
4. Validate tool schemas with simple inputs
5. Check MCP SDK version compatibility

## Best Practices

### Code Style
- Use TypeScript strict mode
- Implement comprehensive error handling
- Add descriptive comments for complex logic
- Follow consistent naming conventions

### Performance
- Use connection pooling for database clients
- Implement lazy loading for optional databases
- Cache frequently accessed metadata
- Monitor and log performance metrics

### Security
- Never log sensitive information
- Validate all inputs with Zod schemas
- Use parameterized queries to prevent injection
- Implement proper authentication for HTTP mode

### Testing
- Test both success and error scenarios
- Validate input schema enforcement
- Test session management and cleanup
- Verify tool responses match expected format
