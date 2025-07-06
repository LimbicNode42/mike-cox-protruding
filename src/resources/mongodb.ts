/**
 * MongoDB Resources for Database MCP Server
 * Complete implementation matching Python version functionality
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig, getOrCreateSession } from '../types/session.js';

export function registerMongoResources(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('🍃 Registering MongoDB resources...');

  // MongoDB server information
  server.registerResource(
    'mongodb-info',
    'mongodb://info',
    {
      name: 'MongoDB Server Info',
      description: 'Get MongoDB server information',
      mimeType: 'application/json'
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.mongodb) {
          return {
            contents: [{
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify({ error: 'MongoDB is disabled in the server configuration' }, null, 2)
            }]
          };
        }
        
        const admin = session.clients.mongodb.db('admin');
        const info = await admin.admin().serverInfo();
        
        return {
          contents: [{
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify({ server_info: info }, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify({ 
              error: `Failed to get MongoDB server info: ${error instanceof Error ? error.message : 'Unknown error'}` 
            }, null, 2)
          }]
        };
      }
    }
  );

  // MongoDB databases
  server.registerResource(
    'mongodb-databases',
    'mongodb://databases',
    {
      name: 'MongoDB Databases',
      description: 'List all MongoDB databases',
      mimeType: 'application/json'
    },
    async (uri: URL) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.mongodb) {
          return {
            contents: [{
              uri: uri.href,
              mimeType: 'application/json',
              text: JSON.stringify({ error: 'MongoDB is disabled in the server configuration' }, null, 2)
            }]
          };
        }
        
        const admin = session.clients.mongodb.db('admin');
        const databases = await admin.admin().listDatabases();
        
        return {
          contents: [{
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify({ databases: databases.databases }, null, 2)
          }]
        };
      } catch (error) {
        return {
          contents: [{
            uri: uri.href,
            mimeType: 'application/json',
            text: JSON.stringify({ 
              error: `Failed to list MongoDB databases: ${error instanceof Error ? error.message : 'Unknown error'}` 
            }, null, 2)
          }]
        };
      }
    }
  );

  console.error('✅ MongoDB resources registered');
}
