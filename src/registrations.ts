/**
 * Database MCP Server - Tool and Resource Registration
 *
 * Registers all database tools and resources with the MCP server.
 * Supports multiple database types with session-aware operations.
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DatabaseSession, DatabaseConfig } from './types/session.js';
import { registerPostgresTools } from './tools/postgres.js';
import { registerRedisTools } from './tools/redis.js';
import { registerMongoTools } from './tools/mongodb.js';
import { registerInfluxTools } from './tools/influxdb.js';
import { registerDatabaseResources } from './resources/index.js';

/**
 * Register all tools and resources with the MCP server
 */
export function registerAllCapabilities(
  server: McpServer,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): void {
  console.error('📋 Registering database tools and resources...');

  // Register PostgreSQL tools (primary database, always enabled)
  registerPostgresTools(server, config, sessions);

  // Register Redis tools if enabled in config
  if (config.redis?.enabled) {
    registerRedisTools(server, config, sessions);
  } else {
    console.error('⚠️  Redis tools not registered - Redis not enabled in config');
  }

  // Register MongoDB tools if enabled in config
  if (config.mongodb?.enabled) {
    registerMongoTools(server, config, sessions);
  } else {
    console.error('⚠️  MongoDB tools not registered - MongoDB not enabled in config');
  }

  // Register InfluxDB tools if enabled in config
  if (config.influxdb?.enabled) {
    registerInfluxTools(server, config, sessions);
  } else {
    console.error('⚠️  InfluxDB tools not registered - InfluxDB not enabled in config');
  }

  // TODO: Register resources when implemented
  // registerDatabaseResources(server, config, sessions);

  // Register database resources
  registerDatabaseResources(server, config, sessions);

  console.error('✅ All database capabilities registered');
}
