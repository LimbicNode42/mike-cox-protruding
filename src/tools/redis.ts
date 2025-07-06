/**
 * Simple Redis Tools for Database MCP Server
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';
import { z } from 'zod';

export function registerRedisTools(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('🔴 Registering Redis tools...');

  server.registerTool(
    'redis_get',
    {
      description: 'Get a value from Redis',
      inputSchema: {
        key: z.string().describe('Redis key to get')
      }
    },
    async (args: { key: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.redis) {
          throw new Error('Redis client not available');
        }
        
        const value = await session.clients.redis.get(args.key);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              key: args.key,
              value,
              exists: value !== null,
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

  console.error('✅ Redis tools registered');
}
