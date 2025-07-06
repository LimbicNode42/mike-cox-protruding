/**
 * Simple MongoDB Tools for Database MCP Server
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';
import { z } from 'zod';

export function registerMongoTools(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('🍃 Registering MongoDB tools...');

  server.registerTool(
    'mongodb_find',
    {
      description: 'Find documents in MongoDB collection',
      inputSchema: {
        database: z.string().describe('Database name'),
        collection: z.string().describe('Collection name'),
        query: z.object({}).optional().describe('Query filter (optional)')
      }
    },
    async (args: { database: string; collection: string; query?: any }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.mongodb) {
          throw new Error('MongoDB client not available');
        }
        
        const db = session.clients.mongodb.db(args.database);
        const coll = db.collection(args.collection);
        const docs = await coll.find(args.query || {}).limit(10).toArray();
        
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              database: args.database,
              collection: args.collection,
              count: docs.length,
              documents: docs,
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

  console.error('✅ MongoDB tools registered');
}
