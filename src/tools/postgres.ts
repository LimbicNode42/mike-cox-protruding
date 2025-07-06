/**
 * Simple PostgreSQL Tools for Database MCP Server
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';
import { z } from 'zod';

export function registerPostgresTools(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('🐘 Registering PostgreSQL tools...');

  server.registerTool(
    'postgres_query',
    {
      description: 'Execute a PostgreSQL query',
      inputSchema: {
        query: z.string().describe('SQL query to execute')
      }
    },
    async (args: { query: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.postgres) {
          throw new Error('PostgreSQL client not available');
        }
        
        const result = await session.clients.postgres.query(args.query);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              rowCount: result.rowCount,
              rows: result.rows,
              success: true
            }, null, 2)
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

  console.error('✅ PostgreSQL tools registered');
}
