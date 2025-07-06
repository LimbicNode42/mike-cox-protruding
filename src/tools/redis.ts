/**
 * Redis Tools for Database MCP Server
 * Complete implementation matching Python version functionality
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

  // Execute a Redis command
  server.registerTool(
    'redis_execute_command',
    {
      description: 'Execute a Redis command',
      inputSchema: {
        command: z.string().describe('Redis command to execute'),
        args: z.array(z.string()).describe('Command arguments').optional()
      }
    },
    async (args: { command: string; args?: string[] | undefined }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.redis) {
          throw new Error('Redis client not available');
        }
        
        const commandArgs = args.args || [];
        const result = await session.clients.redis.call(args.command, ...commandArgs);
        
        return {
          content: [{
            type: 'text',
            text: `Redis command result: ${JSON.stringify(result, null, 2)}`
          }]
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{
            type: 'text',
            text: `Failed to execute Redis command: ${message}`
          }]
        };
      }
    }
  );

  // Set a Redis key-value pair
  server.registerTool(
    'redis_set_key',
    {
      description: 'Set a Redis key-value pair',
      inputSchema: {
        key: z.string().describe('Redis key'),
        value: z.string().describe('Redis value'),
        database: z.number().describe('Redis database number').default(0)
      }
    },
    async (args: { key: string; value: string; database?: number }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.redis) {
          throw new Error('Redis client not available');
        }
        
        const database = args.database || 0;
        await session.clients.redis.select(database);
        const result = await session.clients.redis.set(args.key, args.value);
        
        return {
          content: [{
            type: 'text',
            text: `Redis key '${args.key}' set successfully in database ${database}: ${result}`
          }]
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{
            type: 'text',
            text: `Failed to set Redis key '${args.key}': ${message}`
          }]
        };
      }
    }
  );

  // Delete a Redis key
  server.registerTool(
    'redis_delete_key',
    {
      description: 'Delete a Redis key',
      inputSchema: {
        key: z.string().describe('Redis key to delete'),
        database: z.number().describe('Redis database number').default(0)
      }
    },
    async (args: { key: string; database?: number }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.redis) {
          throw new Error('Redis client not available');
        }
        
        const database = args.database || 0;
        await session.clients.redis.select(database);
        const result = await session.clients.redis.del(args.key);
        
        return {
          content: [{
            type: 'text',
            text: `Redis key '${args.key}' deleted from database ${database}: ${result} key(s) removed`
          }]
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{
            type: 'text',
            text: `Failed to delete Redis key '${args.key}': ${message}`
          }]
        };
      }
    }
  );

  // Flush all keys from a Redis database
  server.registerTool(
    'redis_flush_database',
    {
      description: 'Flush all keys from a Redis database',
      inputSchema: {
        database: z.number().describe('Redis database number to flush').default(0)
      }
    },
    async (args: { database?: number }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.redis) {
          throw new Error('Redis client not available');
        }
        
        const database = args.database || 0;
        await session.clients.redis.select(database);
        const result = await session.clients.redis.flushdb();
        
        return {
          content: [{
            type: 'text',
            text: `Redis database ${database} flushed successfully: ${result}`
          }]
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{
            type: 'text',
            text: `Failed to flush Redis database ${args.database || 0}: ${message}`
          }]
        };
      }
    }
  );

  console.error('✅ Redis tools registered');
}
