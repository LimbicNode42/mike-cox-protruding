/**
 * MongoDB Tools for Database MCP Server
 * Complete implementation matching Python version functionality
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

  // Find documents in a MongoDB collection
  server.registerTool(
    'mongodb_find_documents',
    {
      description: 'Find documents in a MongoDB collection',
      inputSchema: {
        database: z.string().describe('Database name'),
        collection: z.string().describe('Collection name'),
        filter_query: z.string().describe('Filter query as JSON string').default('{}'),
        limit: z.number().describe('Maximum number of documents to return').default(10),
      },
    },
    async (args: {
      database: string;
      collection: string;
      filter_query?: string;
      limit?: number;
    }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.mongodb) {
          throw new Error('MongoDB client not available');
        }

        const filterQuery = args.filter_query || '{}';
        const limit = args.limit || 10;
        const filterDict = JSON.parse(filterQuery);

        const db = session.clients.mongodb.db(args.database);
        const coll = db.collection(args.collection);
        const documents = await coll.find(filterDict).limit(limit).toArray();

        return {
          content: [
            {
              type: 'text',
              text: `MongoDB documents from '${args.collection}': ${JSON.stringify(documents, null, 2)}`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Failed to find MongoDB documents: ${message}`,
            },
          ],
        };
      }
    }
  );

  // Execute MongoDB aggregation pipeline
  server.registerTool(
    'mongodb_aggregate',
    {
      description: 'Execute MongoDB aggregation pipeline',
      inputSchema: {
        database: z.string().describe('Database name'),
        collection: z.string().describe('Collection name'),
        pipeline: z.string().describe('Aggregation pipeline as JSON array string'),
      },
    },
    async (args: { database: string; collection: string; pipeline: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.mongodb) {
          throw new Error('MongoDB client not available');
        }

        const pipelineList = JSON.parse(args.pipeline);
        const db = session.clients.mongodb.db(args.database);
        const coll = db.collection(args.collection);
        const results = await coll.aggregate(pipelineList).toArray();

        return {
          content: [
            {
              type: 'text',
              text: `MongoDB aggregation results: ${JSON.stringify(results, null, 2)}`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Failed to execute MongoDB aggregation: ${message}`,
            },
          ],
        };
      }
    }
  );

  // Insert a document into a MongoDB collection
  server.registerTool(
    'mongodb_insert_document',
    {
      description: 'Insert a document into a MongoDB collection',
      inputSchema: {
        database: z.string().describe('Database name'),
        collection: z.string().describe('Collection name'),
        document: z.string().describe('Document to insert as JSON string'),
      },
    },
    async (args: { database: string; collection: string; document: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.mongodb) {
          throw new Error('MongoDB client not available');
        }

        const docDict = JSON.parse(args.document);
        const db = session.clients.mongodb.db(args.database);
        const coll = db.collection(args.collection);
        const result = await coll.insertOne(docDict);

        return {
          content: [
            {
              type: 'text',
              text: `Document inserted successfully into '${args.collection}': ${result.insertedId}`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Failed to insert MongoDB document: ${message}`,
            },
          ],
        };
      }
    }
  );

  // Update documents in a MongoDB collection
  server.registerTool(
    'mongodb_update_documents',
    {
      description: 'Update documents in a MongoDB collection',
      inputSchema: {
        database: z.string().describe('Database name'),
        collection: z.string().describe('Collection name'),
        filter_query: z.string().describe('Filter query as JSON string'),
        update_query: z.string().describe('Update query as JSON string'),
      },
    },
    async (args: {
      database: string;
      collection: string;
      filter_query: string;
      update_query: string;
    }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.mongodb) {
          throw new Error('MongoDB client not available');
        }

        const filterDict = JSON.parse(args.filter_query);
        const updateDict = JSON.parse(args.update_query);

        const db = session.clients.mongodb.db(args.database);
        const coll = db.collection(args.collection);
        const result = await coll.updateMany(filterDict, updateDict);

        return {
          content: [
            {
              type: 'text',
              text: `Documents updated in '${args.collection}': ${result.modifiedCount} document(s) modified`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Failed to update MongoDB documents: ${message}`,
            },
          ],
        };
      }
    }
  );

  // Delete documents from a MongoDB collection
  server.registerTool(
    'mongodb_delete_documents',
    {
      description: 'Delete documents from a MongoDB collection',
      inputSchema: {
        database: z.string().describe('Database name'),
        collection: z.string().describe('Collection name'),
        filter_query: z.string().describe('Filter query as JSON string'),
      },
    },
    async (args: { database: string; collection: string; filter_query: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.mongodb) {
          throw new Error('MongoDB client not available');
        }

        const filterDict = JSON.parse(args.filter_query);
        const db = session.clients.mongodb.db(args.database);
        const coll = db.collection(args.collection);
        const result = await coll.deleteMany(filterDict);

        return {
          content: [
            {
              type: 'text',
              text: `Documents deleted from '${args.collection}': ${result.deletedCount} document(s) removed`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Failed to delete MongoDB documents: ${message}`,
            },
          ],
        };
      }
    }
  );

  // Create a new collection in a MongoDB database
  server.registerTool(
    'mongodb_create_collection',
    {
      description: 'Create a new collection in a MongoDB database',
      inputSchema: {
        database: z.string().describe('Database name'),
        collection: z.string().describe('Collection name'),
      },
    },
    async (args: { database: string; collection: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.mongodb) {
          throw new Error('MongoDB client not available');
        }

        const db = session.clients.mongodb.db(args.database);
        await db.createCollection(args.collection);

        return {
          content: [
            {
              type: 'text',
              text: `Collection '${args.collection}' created successfully in database '${args.database}'`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Failed to create MongoDB collection '${args.collection}': ${message}`,
            },
          ],
        };
      }
    }
  );

  console.error('✅ MongoDB tools registered');
}
