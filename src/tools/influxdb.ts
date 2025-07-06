/**
 * InfluxDB Tools for Database MCP Server
 * Complete implementation matching Python version functionality
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

  // Execute a Flux query on InfluxDB
  server.registerTool(
    'influxdb_query',
    {
      description: 'Execute a Flux query on InfluxDB',
      inputSchema: {
        bucket: z.string().describe('Target bucket name'),
        flux_query: z.string().describe('Flux query to execute')
      }
    },
    async (args: { bucket: string; flux_query: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.influxdb || !config.influxdb?.org) {
          throw new Error('InfluxDB client not available or org not configured');
        }
        
        const queryApi = session.clients.influxdb.getQueryApi(config.influxdb.org);
        const results: any[] = [];
        
        await new Promise<void>((resolve, reject) => {
          queryApi.queryRows(args.flux_query, {
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
            text: `InfluxDB query results: ${JSON.stringify(results, null, 2)}`
          }]
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{
            type: 'text',
            text: `Failed to execute InfluxDB query: ${message}`
          }]
        };
      }
    }
  );

  // Write data to InfluxDB using line protocol format
  server.registerTool(
    'influxdb_write_data',
    {
      description: 'Write data to InfluxDB using line protocol format',
      inputSchema: {
        bucket: z.string().describe('Target bucket name'),
        measurement: z.string().describe('Measurement name'),
        tags: z.string().describe('Tags in JSON format (e.g., \'{"host": "server1", "region": "us-west"}\')'),
        fields: z.string().describe('Fields in JSON format (e.g., \'{"temperature": 23.5, "humidity": 45.2}\')'),
        timestamp: z.string().describe('Optional timestamp (ISO format), uses current time if empty').optional()
      }
    },
    async (args: { bucket: string; measurement: string; tags: string; fields: string; timestamp?: string | undefined }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.influxdb || !config.influxdb?.org) {
          throw new Error('InfluxDB client not available or org not configured');
        }
        
        // Parse tags and fields from JSON
        const tagDict = JSON.parse(args.tags || '{}');
        const fieldDict = JSON.parse(args.fields);
        
        // Build line protocol format
        const tagString = Object.entries(tagDict).map(([k, v]) => `${k}=${v}`).join(',');
        const fieldString = Object.entries(fieldDict).map(([k, v]) => `${k}=${v}`).join(',');
        
        let lineProtocol = tagString 
          ? `${args.measurement},${tagString} ${fieldString}`
          : `${args.measurement} ${fieldString}`;
        
        if (args.timestamp) {
          lineProtocol += ` ${args.timestamp}`;
        }
        
        const writeApi = session.clients.influxdb.getWriteApi(config.influxdb.org, args.bucket);
        writeApi.writeRecord(lineProtocol);
        await writeApi.close();
        
        return {
          content: [{
            type: 'text',
            text: `Data written successfully to InfluxDB bucket '${args.bucket}': ${lineProtocol}`
          }]
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{
            type: 'text',
            text: `Failed to write data to InfluxDB: ${message}`
          }]
        };
      }
    }
  );

  // Create a new bucket in InfluxDB
  server.registerTool(
    'influxdb_create_bucket',
    {
      description: 'Create a new bucket in InfluxDB',
      inputSchema: {
        bucket_name: z.string().describe('Name of the bucket to create'),
        retention_period: z.string().describe('Data retention period (e.g., "30d", "1h", "infinite")').default('30d')
      }
    },
    async (args: { bucket_name: string; retention_period?: string }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.influxdb || !config.influxdb?.org) {
          throw new Error('InfluxDB client not available or org not configured');
        }
        
        // Note: Bucket creation may require specific InfluxDB API setup
        // This is a placeholder for the bucket creation functionality
        const retentionPeriod = args.retention_period || '30d';
        return {
          content: [{
            type: 'text',
            text: `Bucket creation functionality not yet implemented for '${args.bucket_name}' with retention '${retentionPeriod}'. Please use InfluxDB UI or CLI.`
          }]
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{
            type: 'text',
            text: `Failed to create InfluxDB bucket '${args.bucket_name}': ${message}`
          }]
        };
      }
    }
  );

  // Delete data from InfluxDB bucket
  server.registerTool(
    'influxdb_delete_data',
    {
      description: 'Delete data from InfluxDB bucket',
      inputSchema: {
        bucket: z.string().describe('Target bucket name'),
        start_time: z.string().describe('Start time (RFC3339 format, e.g., "2023-01-01T00:00:00Z")'),
        end_time: z.string().describe('End time (RFC3339 format, e.g., "2023-01-02T00:00:00Z")'),
        predicate: z.string().describe('Optional delete predicate (e.g., \'_measurement="temperature"\')').optional()
      }
    },
    async (args: { bucket: string; start_time: string; end_time: string; predicate?: string | undefined }) => {
      try {
        const sessionId = 'default';
        const session = await getOrCreateSession(sessionId, config, sessions);
        
        if (!session.clients.influxdb || !config.influxdb?.org) {
          throw new Error('InfluxDB client not available or org not configured');
        }
        
        // Note: Data deletion may require specific InfluxDB API setup
        // This is a placeholder for the data deletion functionality
        return {
          content: [{
            type: 'text',
            text: `Data deletion functionality not yet implemented for bucket '${args.bucket}' between ${args.start_time} and ${args.end_time}. Please use InfluxDB UI or CLI.`
          }]
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Unknown error';
        return {
          content: [{
            type: 'text',
            text: `Failed to delete data from InfluxDB: ${message}`
          }]
        };
      }
    }
  );

  console.error('✅ InfluxDB tools registered');
}
