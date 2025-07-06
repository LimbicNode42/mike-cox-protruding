/**
 * Database MCP Server - Main Entry Point
 * 
 * A comprehensive database management MCP server supporting multiple database types:
 * - PostgreSQL (primary)
 * - Redis (caching)
 * - MongoDB (document store)
 * - InfluxDB (time series)
 * 
 * This server follows MC-PEA architectural standards and integrates with
 * Keycloak authentication and Infisical secrets management.
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import express, { Request, Response } from 'express';
import cors from 'cors';
import { randomUUID } from 'crypto';
import dotenv from 'dotenv';
import { isInitializeRequest } from '@modelcontextprotocol/sdk/types.js';
import { registerAllCapabilities } from './registrations.js';
import { DatabaseSession, DatabaseConfig, createDatabaseSession } from './types/session.js';

// Load environment variables
dotenv.config();

// Environment validation
const requiredEnvVars = ['API_KEY'];
const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
if (missingVars.length > 0) {
  console.error(`❌ Missing required environment variables: ${missingVars.join(', ')}`);
  console.error('Please create a .env file based on .env.example');
  process.exit(1);
}

// Configuration
const config: DatabaseConfig = {
  postgres: {
    enabled: process.env.ENABLE_POSTGRES !== 'false',
    url: process.env.POSTGRES_URL || process.env.DATABASE_URL || undefined
  },
  redis: {
    enabled: process.env.ENABLE_REDIS === 'true',
    url: process.env.REDIS_URL || undefined
  },
  mongodb: {
    enabled: process.env.ENABLE_MONGODB === 'true',
    url: process.env.MONGODB_URL || undefined
  },
  influxdb: {
    enabled: process.env.ENABLE_INFLUXDB === 'true',
    url: process.env.INFLUXDB_URL || undefined,
    token: process.env.INFLUXDB_TOKEN || undefined,
    org: process.env.INFLUXDB_ORG || undefined,
    bucket: process.env.INFLUXDB_BUCKET || undefined
  }
};

const serverConfig = {
  port: parseInt(process.env.PORT || '3001'),
  apiKey: process.env.API_KEY!,
  nodeEnv: process.env.NODE_ENV || 'development',
  serverName: 'db-mcp-server',
  serverVersion: '1.0.0'
};

// Session storage for stateful HTTP transport
const sessions: Map<string, DatabaseSession> = new Map();

// Map to store transports by session ID for HTTP mode
const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

/**
 * Generate unique session ID
 */
function sessionIdGenerator(): string {
  return randomUUID();
}

/**
 * Validate API key authentication
 */
function validateAuthentication(apiKey: string): boolean {
  return apiKey === serverConfig.apiKey;
}

/**
 * Initialize database session clients for a session
 */
async function initializeSessionClients(sessionId: string): Promise<DatabaseSession> {
  console.error(`[${sessionId}] Initializing database session`);
  const session = await createDatabaseSession(sessionId, config);
  sessions.set(sessionId, session);
  return session;
}

/**
 * Create a new MCP server instance (stdio mode)
 */
function createServer(): McpServer {
  const server = new McpServer(
    {
      name: serverConfig.serverName,
      version: serverConfig.serverVersion,
    },
    {
      capabilities: {
        tools: {},
        resources: {},
      },
    }
  );

  // Register all tools and resources
  registerAllCapabilities(server, config, sessions);

  return server;
}

/**
 * Create a new MCP server instance for a specific session (HTTP mode)
 */
function createStatefulMCPServer(sessionId: string): McpServer {
  const server = new McpServer(
    {
      name: serverConfig.serverName,
      version: serverConfig.serverVersion,
    },
    {
      capabilities: {
        tools: {},
        resources: {},
      },
    }
  );

  // Get session
  const session = sessions.get(sessionId);
  if (!session) {
    throw new Error(`Session ${sessionId} not found`);
  }

  console.error(`[${sessionId}] Creating MCP server for session`);

  // Register all tools and resources for this session
  registerAllCapabilities(server, config, sessions);

  return server;
}

/**
 * Main execution function
 */
async function main() {
  // Parse command line arguments
  const args = process.argv.slice(2);
  const mode = args.includes('--mode') ? args[args.indexOf('--mode') + 1] : 'stdio';
  const host = args.includes('--host') ? args[args.indexOf('--host') + 1] : '0.0.0.0';
  const port = args.includes('--port')
    ? parseInt(args[args.indexOf('--port') + 1] || serverConfig.port.toString())
    : serverConfig.port;

  console.error(`🚀 Starting ${serverConfig.serverName} v${serverConfig.serverVersion} in ${mode} mode`);
  console.error(`📊 Database support:`);
  console.error(`   PostgreSQL: ${config.postgres.enabled ? '✅' : '❌'}`);
  console.error(`   Redis: ${config.redis?.enabled ? '✅' : '❌'}`);
  console.error(`   MongoDB: ${config.mongodb?.enabled ? '✅' : '❌'}`);
  console.error(`   InfluxDB: ${config.influxdb?.enabled ? '✅' : '❌'}`);

  if (mode === 'http') {
    // HTTP mode for production deployments with session management
    await runStatefulHttpServer(host!, port);
  } else {
    // STDIO mode for MCP Inspector and development
    await runStdioServer();
  }
}

/**
 * Run server in STDIO mode (for development/testing)
 */
async function runStdioServer() {
  // Create a single session for STDIO mode
  const sessionId = 'stdio-session';
  await initializeSessionClients(sessionId);

  const server = createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);
  console.error('✅ Database MCP server connected via stdio transport');
}

/**
 * Run server in HTTP mode with session management (stateful)
 */
async function runStatefulHttpServer(host: string, port: number) {
  const app = express();

  // Enable CORS for all routes
  app.use(
    cors({
      origin: true,
      exposedHeaders: ['mcp-session-id'],
      allowedHeaders: ['Content-Type', 'mcp-session-id', 'API_KEY'],
    })
  );

  // Parse JSON bodies
  app.use(express.json());

  // API Key authentication middleware
  function validateApiKey(req: Request, res: Response, next: any) {
    const requiredApiKey = serverConfig.apiKey;

    // Skip authentication if no API key is configured
    if (!requiredApiKey) {
      console.error('Warning: No API_KEY configured - authentication disabled');
      return next();
    }

    const providedApiKey = req.headers['api_key'] as string;

    if (!providedApiKey) {
      console.error('Authentication failed: Missing API_KEY header');
      return res.status(401).json({
        jsonrpc: '2.0',
        error: {
          code: -32001,
          message: 'Authentication required: Missing API_KEY header',
        },
        id: null,
      });
    }

    if (providedApiKey !== requiredApiKey) {
      console.error('Authentication failed: Invalid API_KEY');
      return res.status(401).json({
        jsonrpc: '2.0',
        error: {
          code: -32001,
          message: 'Authentication failed: Invalid API_KEY',
        },
        id: null,
      });
    }

    // Authentication successful
    console.error('API key authentication successful');
    next();
  }

  // Health check endpoint
  app.get('/health', (req: Request, res: Response) => {
    const activeSessions = Object.keys(transports).length;
    const authenticationEnabled = !!serverConfig.apiKey;
    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      mode: 'stateful',
      activeSessions,
      capabilities: ['postgresql', 'redis', 'mongodb', 'influxdb'],
      databases: {
        postgres: config.postgres.enabled,
        redis: config.redis?.enabled || false,
        mongodb: config.mongodb?.enabled || false,
        influxdb: config.influxdb?.enabled || false,
      },
      authentication: {
        enabled: authenticationEnabled,
        type: authenticationEnabled ? 'API_KEY' : 'none',
      },
    });
  });

  // Handle POST requests for client-to-server communication
  app.post('/mcp', validateApiKey, async (req: Request, res: Response) => {
    // Check for existing session ID
    const sessionId = req.headers['mcp-session-id'] as string | undefined;
    let transport: StreamableHTTPServerTransport;
    let server: McpServer;

    if (sessionId && transports[sessionId]) {
      // Reuse existing transport and session
      transport = transports[sessionId];
      console.error(`[${sessionId}] Reusing existing session`);
    } else if (!sessionId && isInitializeRequest(req.body)) {
      // New initialization request - create new session
      const newSessionId = randomUUID();
      console.error(`[${newSessionId}] Creating new session`);

      // Initialize session clients
      await initializeSessionClients(newSessionId);

      // Create stateful server for this session
      server = createStatefulMCPServer(newSessionId);

      // Create transport with session management
      // Configure DNS rebinding protection and allowed hosts
      const enableDnsRebindingProtection =
        process.env.MCP_ENABLE_DNS_REBINDING_PROTECTION !== 'false';
      const allowedHosts: string[] = [];

      if (enableDnsRebindingProtection) {
        // Start with default localhost addresses
        allowedHosts.push('127.0.0.1', 'localhost', `127.0.0.1:${port}`, `localhost:${port}`);

        // Add the current host if not localhost
        if (host !== '127.0.0.1' && host !== 'localhost') {
          allowedHosts.push(host, `${host}:${port}`);
        }

        // Add custom allowed hosts from environment variable
        const customHosts = process.env.MCP_ALLOWED_HOSTS;
        if (customHosts) {
          allowedHosts.push(...customHosts.split(',').map(h => h.trim()));
        }

        console.error(
          `[${newSessionId}] DNS rebinding protection ENABLED. Allowed hosts: ${allowedHosts.join(', ')}`
        );
      } else {
        console.error(`[${newSessionId}] DNS rebinding protection DISABLED - allowing all hosts`);
      }

      const transportOptions: any = {
        sessionIdGenerator: () => newSessionId,
        onsessioninitialized: (id: string) => {
          console.error(`[${id}] Session initialized`);
          transports[id] = transport;
        },
        enableDnsRebindingProtection,
      };

      if (enableDnsRebindingProtection) {
        transportOptions.allowedHosts = allowedHosts;
      }

      transport = new StreamableHTTPServerTransport(transportOptions);

      // Clean up transport when closed
      transport.onclose = () => {
        console.error(`[${newSessionId}] Session closed, cleaning up`);
        if (transport.sessionId) {
          delete transports[transport.sessionId];
          const session = sessions.get(transport.sessionId);
          if (session) {
            session.cleanup().catch(err => 
              console.error(`Error cleaning up session ${transport.sessionId}:`, err)
            );
            sessions.delete(transport.sessionId);
          }
        }
      };

      // Connect to the MCP server
      await server.connect(transport);
    } else {
      // Invalid request
      console.error('Invalid request: No valid session ID provided');
      res.status(400).json({
        jsonrpc: '2.0',
        error: {
          code: -32000,
          message: 'Bad Request: No valid session ID provided',
        },
        id: null,
      });
      return;
    }

    try {
      // Handle the request
      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error('Error handling MCP request:', error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: '2.0',
          error: {
            code: -32603,
            message: 'Internal server error',
          },
          id: null,
        });
      }
    }
  });

  // Handle GET requests for server-to-client notifications via SSE
  app.get('/mcp', validateApiKey, async (req: Request, res: Response) => {
    const sessionId = req.headers['mcp-session-id'] as string | undefined;
    if (!sessionId || !transports[sessionId]) {
      res.status(400).send('Invalid or missing session ID');
      return;
    }

    const transport = transports[sessionId];
    await transport.handleRequest(req, res);
  });

  // Handle DELETE requests for session termination
  app.delete('/mcp', validateApiKey, async (req: Request, res: Response) => {
    const sessionId = req.headers['mcp-session-id'] as string | undefined;
    if (!sessionId || !transports[sessionId]) {
      res.status(400).send('Invalid or missing session ID');
      return;
    }

    const transport = transports[sessionId];
    await transport.handleRequest(req, res);
  });

  app.listen(port, host, () => {
    const authEnabled = !!serverConfig.apiKey;
    console.error(
      `✅ Database MCP Server started in STATEFUL HTTP mode on ${host}:${port}`
    );
    console.error(`🔍 Health check available at: http://${host}:${port}/health`);
    console.error(`🔌 MCP endpoint available at: http://${host}:${port}/mcp`);
    console.error(
      `🔐 Authentication: ${authEnabled ? 'ENABLED (API_KEY required)' : 'DISABLED (no API_KEY configured)'}`
    );
    console.error('📊 Features: Session management, SSE notifications, stateful client connections');
  });
}

// Graceful shutdown handling
process.on('SIGINT', async () => {
  console.error('🛑 Shutting down database MCP server...');
  
  // Clean up all database connections
  for (const [sessionId, session] of sessions) {
    try {
      await session.cleanup();
      console.error(`✅ Cleaned up session: ${sessionId}`);
    } catch (error) {
      console.error(`❌ Error cleaning up session ${sessionId}:`, error);
    }
  }
  
  sessions.clear();
  process.exit(0);
});

// Handle unhandled rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
  process.exit(1);
});

// Run the server immediately when this module is executed
main().catch(error => {
  console.error('❌ Failed to start database MCP server:', error);
  process.exit(1);
});

export { createServer, config, serverConfig };
