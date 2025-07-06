/**
 * PostgreSQL Tools for Database MCP Server
 * Complete implementation matching Python version functionality
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

  // Execute a PostgreSQL query (SELECT)
  server.registerTool(
    'postgres_query',
    {
      description: 'Execute a SQL query on PostgreSQL and return the results',
      inputSchema: {
        sql: z.string().describe('SQL query to execute'),
        database: z.string().describe('Target database name').default('postgres'),
      },
    },
    async (args: { sql: string; database?: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.postgres) {
          throw new Error('PostgreSQL client not available');
        }

        const database = args.database || 'postgres';
        const result = await session.clients.postgres.query(args.sql);

        return {
          content: [
            {
              type: 'text',
              text: `Query executed successfully on PostgreSQL '${database}'. Results: ${JSON.stringify(result.rows, null, 2)}`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `PostgreSQL query failed on '${args.database || 'postgres'}': ${message}`,
            },
          ],
        };
      }
    }
  );

  // Execute INSERT, UPDATE, DELETE, or DDL statements
  server.registerTool(
    'postgres_execute',
    {
      description: 'Execute INSERT, UPDATE, DELETE, or DDL statements on PostgreSQL',
      inputSchema: {
        sql: z.string().describe('SQL statement to execute'),
        database: z.string().describe('Target database name').default('postgres'),
      },
    },
    async (args: { sql: string; database?: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.postgres) {
          throw new Error('PostgreSQL client not available');
        }

        const database = args.database || 'postgres';
        const result = await session.clients.postgres.query(args.sql);

        return {
          content: [
            {
              type: 'text',
              text: `SQL executed successfully on PostgreSQL '${database}': ${result.rowCount || 0} rows affected`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `PostgreSQL SQL execution failed on '${args.database || 'postgres'}': ${message}`,
            },
          ],
        };
      }
    }
  );

  // Create a new table
  server.registerTool(
    'postgres_create_table',
    {
      description: 'Create a new table in PostgreSQL database',
      inputSchema: {
        database: z.string().describe('Target database name'),
        table_name: z.string().describe('Name of the table to create'),
        columns: z
          .string()
          .describe(
            'Column definitions (e.g., "id SERIAL PRIMARY KEY, name VARCHAR(100), email VARCHAR(255)")'
          ),
      },
    },
    async (args: { database: string; table_name: string; columns: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.postgres) {
          throw new Error('PostgreSQL client not available');
        }

        const sql = `CREATE TABLE ${args.table_name} (${args.columns})`;
        const result = await session.clients.postgres.query(sql);

        return {
          content: [
            {
              type: 'text',
              text: `Table '${args.table_name}' created successfully in PostgreSQL '${args.database}': ${result.rowCount || 0} rows affected`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Failed to create table '${args.table_name}' in PostgreSQL '${args.database}': ${message}`,
            },
          ],
        };
      }
    }
  );

  // Create a new database
  server.registerTool(
    'postgres_create_database',
    {
      description: 'Create a new PostgreSQL database',
      inputSchema: {
        database_name: z.string().describe('Name of the database to create'),
      },
    },
    async (args: { database_name: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);

        if (!session.clients.postgres) {
          throw new Error('PostgreSQL client not available');
        }

        const sql = `CREATE DATABASE ${args.database_name}`;
        const result = await session.clients.postgres.query(sql);

        return {
          content: [
            {
              type: 'text',
              text: `Database '${args.database_name}' created successfully: ${result.rowCount || 0} rows affected`,
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [
            {
              type: 'text',
              text: `Failed to create PostgreSQL database '${args.database_name}': ${message}`,
            },
          ],
        };
      }
    }
  );

  console.error('✅ PostgreSQL tools registered');
}
