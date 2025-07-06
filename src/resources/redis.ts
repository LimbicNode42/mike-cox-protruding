/**
 * Redis Resources for Database MCP Server
 * Complete implementation matching Python version functionality
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';

export function registerRedisResources(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('🔴 Registering Redis resources...');

  // Redis server information
  server.registerResource(
    'redis-info',
    'redis://info',
    {
      name: 'Redis Server Info',
      description: 'Get Redis server information',
      mimeType: 'application/json',
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.redis) {
          return {
            contents: [
              {
                uri: uri.href,
                mimeType: 'application/json',
                text: JSON.stringify(
                  { error: 'Redis is disabled in the server configuration' },
                  null,
                  2
                ),
              },
            ],
          };
        }

        const info = await session.clients.redis.info();

        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify({ server_info: info }, null, 2),
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
                  error: `Failed to get Redis info: ${error instanceof Error ? error.message : 'Unknown error'}`,
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

  // Redis databases with data
  server.registerResource(
    'redis-databases',
    'redis://databases',
    {
      name: 'Redis Databases',
      description: 'List Redis databases with data',
      mimeType: 'application/json',
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.redis) {
          return {
            contents: [
              {
                uri: uri.href,
                mimeType: 'application/json',
                text: JSON.stringify(
                  { error: 'Redis is disabled in the server configuration' },
                  null,
                  2
                ),
              },
            ],
          };
        }

        // Check databases 0-15 for keys
        const databases = [];
        for (let i = 0; i < 16; i++) {
          try {
            await session.clients.redis.select(i);
            const dbsize = await session.clients.redis.dbsize();
            if (dbsize > 0) {
              databases.push({ database: i, keys: dbsize });
            }
          } catch (error) {
            // Skip databases that don't exist or can't be accessed
          }
        }

        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify({ databases }, null, 2),
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
                  error: `Failed to list Redis databases: ${error instanceof Error ? error.message : 'Unknown error'}`,
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

  console.error('✅ Redis resources registered');
}
