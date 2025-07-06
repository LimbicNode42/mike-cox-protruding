/**
 * Simple InfluxDB Tools for Database MCP Server
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';
import { z } from 'zod';

export function registerInfluxTools(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('📈 Registering InfluxDB tools...');

  server.registerTool(
    'influxdb_query',
    {
      description: 'Query InfluxDB with Flux query language',
      inputSchema: {
        query: z.string().describe('Flux query to execute')
      }
    },
    async (args: { query: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.influxdb || !config.influxdb?.org) {
          throw new Error('InfluxDB client not available or org not configured');
        }
        
        const queryApi = session.clients.influxdb.getQueryApi(config.influxdb.org);
        const results: any[] = [];
        
        await new Promise<void>((resolve, reject) => {
          queryApi.queryRows(args.query, {
            next(row: string[], tableMeta: any) {
              const o = tableMeta.toObject(row);
              results.push(o);
            },
            error: reject,
            complete: () => resolve()
          });
        });
        
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              query: args.query,
              count: results.length,
              results,
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

  console.error('✅ InfluxDB tools registered');
}
