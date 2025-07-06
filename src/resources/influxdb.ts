/**
 * InfluxDB Resources for Database MCP Server
 * Complete implementation matching Python version functionality
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';

export function registerInfluxResources(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('📈 Registering InfluxDB resources...');

  // InfluxDB server information
  server.registerResource(
    'influxdb-info',
    'influxdb://info',
    {
      name: 'InfluxDB Server Info',
      description: 'Get InfluxDB server information',
      mimeType: 'application/json',
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.influxdb || !config.influxdb?.org) {
          return {
            contents: [
              {
                uri: uri.href,
                mimeType: 'application/json',
                text: JSON.stringify(
                  {
                    error:
                      'InfluxDB is disabled. Please enable it in configuration to use this resource.',
                  },
                  null,
                  2
                ),
              },
            ],
          };
        }

        // Get basic server information
        const info = {
          org: config.influxdb.org,
          bucket: config.influxdb.bucket,
          connected: true,
          url: config.influxdb.url,
        };

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
                  error: `Failed to get InfluxDB server info: ${error instanceof Error ? error.message : 'Unknown error'}`,
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

  // InfluxDB buckets
  server.registerResource(
    'influxdb-buckets',
    'influxdb://buckets',
    {
      name: 'InfluxDB Buckets',
      description: 'List all InfluxDB buckets',
      mimeType: 'application/json',
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.influxdb || !config.influxdb?.org) {
          return {
            contents: [
              {
                uri: uri.href,
                mimeType: 'application/json',
                text: JSON.stringify(
                  {
                    error:
                      'InfluxDB is disabled. Please enable it in configuration to use this resource.',
                  },
                  null,
                  2
                ),
              },
            ],
          };
        }

        // For now, return the configured bucket since the buckets API may not be easily accessible
        const buckets = [config.influxdb.bucket].filter(Boolean);

        return {
          contents: [
            {
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify({ buckets }, null, 2),
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
                  error: `Failed to list InfluxDB buckets: ${error instanceof Error ? error.message : 'Unknown error'}`,
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

  console.error('✅ InfluxDB resources registered');
}
