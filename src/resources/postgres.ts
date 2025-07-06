/**
 * PostgreSQL Resources for Database MCP Server
 * Complete implementation matching Python version functionality
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';

export function registerPostgresResources(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('🐘 Registering PostgreSQL resources...');

  // List all connected PostgreSQL databases
  server.registerResource(
    'postgres-databases',
    'postgres://databases',
    {
      name: 'PostgreSQL Databases',
      description: 'List all connected PostgreSQL databases',
      mimeType: 'application/json'
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.postgres) {
          return {
            contents: [{
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify({ error: 'PostgreSQL is disabled in the server configuration' }, null, 2)
            }]
          };
        }
        
        // Get list of databases
        const result = await session.clients.postgres.query('SELECT datname FROM pg_database WHERE datallowconn = true ORDER BY datname');
        const databases = result.rows.map((row: any) => row.datname);
        
        return {
          contents: [{
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify({ databases }, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify({ 
              error: `Failed to list PostgreSQL databases: ${error instanceof Error ? error.message : 'Unknown error'}` 
            }, null, 2)
          }]
        };
      }
    }
  );

  // PostgreSQL connection information
  server.registerResource(
    'postgres-connection',
    'postgres://connection',
    {
      name: 'PostgreSQL Connection Info',
      description: 'Get PostgreSQL connection information',
      mimeType: 'application/json'
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.postgres) {
          return {
            contents: [{
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify({ error: 'PostgreSQL is disabled in the server configuration' }, null, 2)
            }]
          };
        }
        
        const connectionInfo = {
          host: config.postgres.url ? new URL(config.postgres.url).hostname : 'localhost',
          port: config.postgres.url ? new URL(config.postgres.url).port : '5432',
          user: config.postgres.url ? new URL(config.postgres.url).username : 'postgres',
          connected: true
        };
        
        return {
          contents: [{
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify({ connection: connectionInfo }, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify({ 
              error: `Failed to get PostgreSQL connection info: ${error instanceof Error ? error.message : 'Unknown error'}` 
            }, null, 2)
          }]
        };
      }
    }
  );

  console.error('✅ PostgreSQL resources registered');
}
