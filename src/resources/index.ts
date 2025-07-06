/**
 * Database MCP Server - Resource Registration
 *
 * Registers all database resources with the MCP server.
 * Organized by database type for better maintainability.
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';
import { registerPostgresResources } from './postgres.js';
import { registerRedisResources } from './redis.js';
import { registerMongoResources } from './mongodb.js';
import { registerInfluxResources } from './influxdb.js';

/**
 * Register all database resources with the MCP server
 */
export function registerDatabaseResources(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('📚 Registering database resources...');

  // Register PostgreSQL resources (primary database, always enabled)
  registerPostgresResources(server, config, sessions);

  // Register Redis resources if enabled in config
  if (config.redis?.enabled) {
    registerRedisResources(server, config, sessions);
  }

  // Register MongoDB resources if enabled in config
  if (config.mongodb?.enabled) {
    registerMongoResources(server, config, sessions);
  }

  // Register InfluxDB resources if enabled in config
  if (config.influxdb?.enabled) {
    registerInfluxResources(server, config, sessions);
  }

  // ========== GENERAL RESOURCES ==========

  // Database connection status resource
  server.registerResource(
    'connection-status',
    'db://connections/status',
    {
      name: 'Database Connection Status',
      description: 'Current status of all database connections',
      mimeType: 'application/json',
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        const status = {
          postgres: {
            enabled: true,
            connected: !!session.clients.postgres,
            config: {
              host: config.postgres.url ? new URL(config.postgres.url).hostname : 'localhost',
              port: config.postgres.url ? new URL(config.postgres.url).port : '5432',
            },
          },
          redis: {
            enabled: !!config.redis?.enabled,
            connected: !!session.clients.redis,
            config: config.redis?.enabled
              ? {
                  url: config.redis.url || 'redis://localhost:6379',
                }
              : null,
          },
          mongodb: {
            enabled: !!config.mongodb?.enabled,
            connected: !!session.clients.mongodb,
            config: config.mongodb?.enabled
              ? {
                  url: config.mongodb.url || 'mongodb://localhost:27017',
                }
              : null,
          },
          influxdb: {
            enabled: !!config.influxdb?.enabled,
            connected: !!session.clients.influxdb,
            config: config.influxdb?.enabled
              ? {
                  url: config.influxdb.url,
                  org: config.influxdb.org,
                  bucket: config.influxdb.bucket,
                }
              : null,
          },
        };

        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify({ status }, null, 2),
            },
          ],
        };
      } catch (error) {
        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify(
                {
                  error: `Failed to get connection status: ${error instanceof Error ? error.message : 'Unknown error'}`,
                },
                null,
                2
              ),
            },
          ],
        };
      }
    }
  );

  console.error('✅ All database resources registered');
}
