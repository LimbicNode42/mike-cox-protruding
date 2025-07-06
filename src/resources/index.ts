/**
 * Database MCP Server - Resource Registration
 * 
 * Provides resources for database schema, connection status, and metadata.
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig } from '../types/session.js';
import { McpError, ErrorCode } from '@modelcontextprotocol/sdk/types.js';

/**
 * Register all database resources with the MCP server
 */
export function registerDatabaseResources(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('📚 Registering database resources...');

  // Database connection status resource
  server.registerResource(
    'connection-status',
    'db://connections/status',
    {
      name: 'Database Connection Status',
      description: 'Current status of all database connections',
      mimeType: 'application/json'
    },
    async (uri: URL) => {
      try {
        const status = {
          timestamp: new Date().toISOString(),
          databases: {
            postgres: {
              enabled: config.postgres.enabled,
              configured: !!config.postgres.url,
              connected: false
            },
            redis: {
              enabled: config.redis?.enabled || false,
              configured: !!config.redis?.url,
              connected: false
            },
            mongodb: {
              enabled: config.mongodb?.enabled || false,
              configured: !!config.mongodb?.url,
              connected: false
            },
            influxdb: {
              enabled: config.influxdb?.enabled || false,
              configured: !!(config.influxdb?.url && config.influxdb?.token),
              connected: false
            }
          },
          activeSessions: sessions.size
        };

        // Check actual connection status for active sessions
        for (const [sessionId, session] of sessions) {
          if (session.clients.postgres) {
            status.databases.postgres.connected = true;
          }
          if (session.clients.redis) {
            status.databases.redis.connected = true;
          }
          if (session.clients.mongodb) {
            status.databases.mongodb.connected = true;
          }
          if (session.clients.influxdb) {
            status.databases.influxdb.connected = true;
          }
        }

        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify(status, null, 2)
            }
          ]
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to get connection status: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    }
  );

  // Database configuration resource
  server.registerResource(
    'config-current',
    'db://config/current',
    {
      name: 'Database Configuration',
      description: 'Current database configuration (without sensitive data)',
      mimeType: 'application/json'
    },
    async (uri: URL) => {
      try {
        const safeConfig = {
          postgres: {
            enabled: config.postgres.enabled,
            hasUrl: !!config.postgres.url
          },
          redis: {
            enabled: config.redis?.enabled || false,
            hasUrl: !!config.redis?.url
          },
          mongodb: {
            enabled: config.mongodb?.enabled || false,
            hasUrl: !!config.mongodb?.url
          },
          influxdb: {
            enabled: config.influxdb?.enabled || false,
            hasUrl: !!config.influxdb?.url,
            hasToken: !!config.influxdb?.token,
            org: config.influxdb?.org,
            bucket: config.influxdb?.bucket
          }
        };

        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify(safeConfig, null, 2)
            }
          ]
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to get configuration: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    }
  );

  // Server capabilities resource
  server.registerResource(
    'server-capabilities',
    'db://server/capabilities',
    {
      name: 'Server Capabilities',
      description: 'Available database server capabilities and tools',
      mimeType: 'application/json'
    },
    async (uri: URL) => {
      try {
        const capabilities = {
          server: {
            name: 'db-mcp-server',
            version: '1.0.0',
            description: 'Database MCP Server supporting PostgreSQL, Redis, MongoDB, and InfluxDB'
          },
          supportedDatabases: {
            postgresql: {
              enabled: config.postgres.enabled,
              tools: ['postgres_query', 'postgres_execute', 'postgres_create_table', 'postgres_create_database'],
              description: 'Primary relational database with full SQL support'
            },
            redis: {
              enabled: config.redis?.enabled || false,
              tools: ['redis_get', 'redis_set', 'redis_delete', 'redis_keys'],
              description: 'In-memory data structure store for caching'
            },
            mongodb: {
              enabled: config.mongodb?.enabled || false,
              tools: ['mongodb_find', 'mongodb_insert', 'mongodb_update', 'mongodb_delete'],
              description: 'Document-oriented NoSQL database'
            },
            influxdb: {
              enabled: config.influxdb?.enabled || false,
              tools: ['influxdb_write', 'influxdb_query', 'influxdb_delete'],
              description: 'Time series database for metrics and events'
            }
          },
          resources: [
            'db://connections/status',
            'db://config/current',
            'db://server/capabilities',
            'db://sessions/active'
          ]
        };

        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify(capabilities, null, 2)
            }
          ]
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to get capabilities: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    }
  );

  // Active sessions resource
  server.registerResource(
    'sessions-active',
    'db://sessions/active',
    {
      name: 'Active Sessions',
      description: 'Information about currently active database sessions',
      mimeType: 'application/json'
    },
    async (uri: URL) => {
      try {
        const sessionInfo = [];
        for (const [sessionId, session] of sessions) {
          sessionInfo.push({
            sessionId,
            createdAt: session.createdAt,
            connectedDatabases: {
              postgres: !!session.clients.postgres,
              redis: !!session.clients.redis,
              mongodb: !!session.clients.mongodb,
              influxdb: !!session.clients.influxdb
            }
          });
        }

        const activeSessionsData = {
          timestamp: new Date().toISOString(),
          totalSessions: sessions.size,
          sessions: sessionInfo
        };

        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify(activeSessionsData, null, 2)
            }
          ]
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Failed to get active sessions: ${error instanceof Error ? error.message : 'Unknown error'}`
        );
      }
    }
  );

  console.error('✅ Database resources registered');
}