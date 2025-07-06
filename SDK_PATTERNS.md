# Database MCP Server - SDK Patterns

This document describes the patterns and best practices used in the Database MCP Server implementation, following the official Model Context Protocol TypeScript SDK.

## Architecture Overview

The Database MCP Server follows a modular architecture with clear separation of concerns:

```
src/
├── index.ts           # Main server entry point and transport setup
├── registrations.ts   # Centralized tool and resource registration
├── types/             # TypeScript type definitions
│   └── session.ts     # Session management and database clients
├── tools/             # Tool implementations by database type
│   ├── postgres.ts    # PostgreSQL tools
│   ├── redis.ts       # Redis tools
│   ├── mongodb.ts     # MongoDB tools
│   └── influxdb.ts    # InfluxDB tools
└── resources/         # Resource implementations (planned)
    └── index.ts       # Database schema and metadata resources
```

## Key SDK Patterns

### 1. Server Creation and Configuration

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

const server = new McpServer(
  {
    name: 'db-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);
```

### 2. Transport Setup

#### Standard I/O Transport
```typescript
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const transport = new StdioServerTransport();
await server.connect(transport);
```

#### HTTP Transport (Planned)
```typescript
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';

const transport = new StreamableHTTPServerTransport({
  // Configuration options
});
await server.connect(transport);
```

### 3. Tool Registration Pattern

The server uses a consistent pattern for registering tools:

```typescript
import { z } from 'zod';

server.registerTool(
  'tool_name',
  {
    description: 'Tool description',
    inputSchema: {
      field: z.string().describe('Field description')
    }
  },
  async (args: { field: string }) => {
    try {
      // Tool implementation
      const result = await performOperation(args);
      
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ error: message, success: false }, null, 2)
        }]
      };
    }
  }
);
```

### 4. Session Management Pattern

The server implements session-based database connection management:

```typescript
export interface DatabaseSession {
  id: string;
  createdAt: Date;
  clients: DatabaseClients;
  cleanup(): Promise<void>;
}

export interface DatabaseClients {
  postgres?: PostgresClient;
  redis?: Redis;
  mongodb?: MongoClient;
  influxdb?: InfluxDB;
}
```

#### Session Creation
```typescript
export async function createDatabaseSession(
  sessionId: string,
  config: DatabaseConfig
): Promise<DatabaseSession> {
  const clients = await initializeSessionClients(config);
  
  return {
    id: sessionId,
    createdAt: new Date(),
    clients,
    async cleanup() {
      // Close all database connections
      await cleanupConnections(clients);
    }
  };
}
```

### 5. Database Client Initialization

Each database type follows a consistent initialization pattern:

```typescript
async function initializeSessionClients(
  config: DatabaseConfig
): Promise<DatabaseClients> {
  const clients: DatabaseClients = {};
  
  // PostgreSQL
  if (config.postgres.enabled && config.postgres.url) {
    try {
      const postgres = new PostgresClient({
        connectionString: config.postgres.url,
        ssl: config.postgres.url.includes('localhost') ? false : { rejectUnauthorized: false }
      });
      await postgres.connect();
      clients.postgres = postgres;
    } catch (error) {
      console.error('Failed to connect to PostgreSQL:', error);
    }
  }
  
  // Similar patterns for Redis, MongoDB, InfluxDB...
  
  return clients;
}
```

### 6. Error Handling Pattern

Consistent error handling across all tools:

```typescript
try {
  // Database operation
  const result = await client.operation(args);
  return { 
    content: [{ 
      type: 'text', 
      text: JSON.stringify({ ...result, success: true }, null, 2) 
    }] 
  };
} catch (error) {
  const message = error instanceof Error ? error.message : 'Unknown error';
  return { 
    content: [{ 
      type: 'text', 
      text: JSON.stringify({ error: message, success: false }, null, 2) 
    }] 
  };
}
```

### 7. Configuration Pattern

Environment-based configuration with type safety:

```typescript
export interface DatabaseConfig {
  postgres: {
    enabled: boolean;
    url?: string;
  };
  redis?: {
    enabled: boolean;
    url?: string;
  };
  // ... other database configurations
}

const config: DatabaseConfig = {
  postgres: {
    enabled: process.env.ENABLE_POSTGRES !== 'false',
    url: process.env.POSTGRES_URL || process.env.DATABASE_URL
  },
  redis: {
    enabled: process.env.ENABLE_REDIS === 'true',
    url: process.env.REDIS_URL
  }
  // ...
};
```

## Best Practices

### 1. Zod Schema Validation
- Use Zod for input schema definition and validation
- Provide clear descriptions for all fields
- Make optional parameters truly optional

### 2. Session Management
- Use session-based connection pooling
- Implement proper cleanup on session end
- Handle connection failures gracefully

### 3. Error Responses
- Always return structured error responses
- Include helpful error messages
- Maintain consistent response format

### 4. TypeScript Types
- Define clear interfaces for all data structures
- Use strict type checking
- Export types for external use

### 5. Logging
- Use console.error for server-side logging
- Include session IDs in log messages
- Log connection status and errors

## Testing Patterns

### Unit Testing
```typescript
import { createServer } from '../src/index.js';

test('server creation', () => {
  const server = createServer();
  expect(server).toBeDefined();
});
```

### Integration Testing
```typescript
// Test actual tool execution with mocked database clients
const mockSession = createMockSession();
const result = await postgresQuery({ query: 'SELECT 1' }, mockSession);
expect(result.success).toBe(true);
```

## Future Enhancements

1. **Resource Implementation** - Add read-only database schema resources
2. **HTTP Transport** - Complete HTTP transport implementation
3. **Authentication** - Integrate with Keycloak/Infisical
4. **Performance Monitoring** - Add metrics and health checks
5. **Connection Pooling** - Optimize database connection management
