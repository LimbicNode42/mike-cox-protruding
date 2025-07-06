/**
 * Database Session Types and Management
 * 
 * Defines session structures and client initialization for database connections.
 * Supports multiple database types with proper connection management and cleanup.
 */

import { Client as PostgresClient } from 'pg';
import Redis from 'ioredis';
import { MongoClient } from 'mongodb';
import { InfluxDB } from '@influxdata/influxdb-client';

/**
 * Configuration interface for database connections
 */
export interface DatabaseConfig {
  postgres: {
    enabled: boolean;
    url?: string | undefined;
  };
  redis?: {
    enabled: boolean;
    url?: string | undefined;
  };
  mongodb?: {
    enabled: boolean;
    url?: string | undefined;
  };
  influxdb?: {
    enabled: boolean;
    url?: string | undefined;
    token?: string | undefined;
    org?: string | undefined;
    bucket?: string | undefined;
  };
}

/**
 * Database clients for a session
 */
export interface DatabaseClients {
  postgres?: PostgresClient;
  redis?: Redis;
  mongodb?: MongoClient;
  influxdb?: InfluxDB;
}

/**
 * Session data for database MCP server
 */
export interface DatabaseSession {
  id: string;
  createdAt: Date;
  clients: DatabaseClients;
  cleanup(): Promise<void>;
}

/**
 * Initialize database clients for a session
 */
export async function initializeSessionClients(
  config: DatabaseConfig
): Promise<DatabaseClients> {
  const clients: DatabaseClients = {};
  
  // Initialize PostgreSQL client
  if (config.postgres.enabled && config.postgres.url) {
    try {
      const postgres = new PostgresClient({
        connectionString: config.postgres.url,
        ssl: config.postgres.url.includes('localhost') ? false : { rejectUnauthorized: false }
      });
      await postgres.connect();
      clients.postgres = postgres;
      console.error(`PostgreSQL client connected`);
    } catch (error) {
      console.error(`Failed to connect to PostgreSQL:`, error);
    }
  }

  // Initialize Redis client
  if (config.redis?.enabled && config.redis.url) {
    try {
      const redis = new Redis(config.redis.url);
      await redis.ping();
      clients.redis = redis;
      console.error(`Redis client connected`);
    } catch (error) {
      console.error(`Failed to connect to Redis:`, error);
    }
  }

  // Initialize MongoDB client
  if (config.mongodb?.enabled && config.mongodb.url) {
    try {
      const mongodb = new MongoClient(config.mongodb.url);
      await mongodb.connect();
      clients.mongodb = mongodb;
      console.error(`MongoDB client connected`);
    } catch (error) {
      console.error(`Failed to connect to MongoDB:`, error);
    }
  }

  // Initialize InfluxDB client
  if (config.influxdb?.enabled && config.influxdb.url && config.influxdb.token) {
    try {
      const influxdb = new InfluxDB({
        url: config.influxdb.url,
        token: config.influxdb.token
      });
      clients.influxdb = influxdb;
      console.error(`InfluxDB client connected`);
    } catch (error) {
      console.error(`Failed to connect to InfluxDB:`, error);
    }
  }

  return clients;
}

/**
 * Create a database session with initialized clients
 */
export async function createDatabaseSession(
  sessionId: string,
  config: DatabaseConfig
): Promise<DatabaseSession> {
  const clients = await initializeSessionClients(config);
  
  return {
    id: sessionId,
    createdAt: new Date(),
    clients,
    async cleanup() {
      // Close all database connections
      if (clients.postgres) {
        try {
          await clients.postgres.end();
          console.error(`[${sessionId}] PostgreSQL connection closed`);
        } catch (error) {
          console.error(`[${sessionId}] Error closing PostgreSQL:`, error);
        }
      }

      if (clients.redis) {
        try {
          clients.redis.disconnect();
          console.error(`[${sessionId}] Redis connection closed`);
        } catch (error) {
          console.error(`[${sessionId}] Error closing Redis:`, error);
        }
      }

      if (clients.mongodb) {
        try {
          await clients.mongodb.close();
          console.error(`[${sessionId}] MongoDB connection closed`);
        } catch (error) {
          console.error(`[${sessionId}] Error closing MongoDB:`, error);
        }
      }

      // InfluxDB client doesn't need explicit cleanup
      if (clients.influxdb) {
        console.error(`[${sessionId}] InfluxDB client cleanup (no explicit disconnect needed)`);
      }
    }
  };
}

/**
 * Get or create a session with database clients
 */
export async function getOrCreateSession(
  sessionId: string,
  config: DatabaseConfig,
  sessions: Map<string, DatabaseSession>
): Promise<DatabaseSession> {
  let session = sessions.get(sessionId);
  
  if (!session) {
    console.error(`Creating new session: ${sessionId}`);
    session = await createDatabaseSession(sessionId, config);
    sessions.set(sessionId, session);
  }

  return session;
}

/**
 * Clean up expired sessions
 */
export async function cleanupExpiredSessions(
  sessions: Map<string, DatabaseSession>,
  maxAgeMs: number = 30 * 60 * 1000 // 30 minutes default
): Promise<void> {
  const now = new Date();
  const expiredSessions: string[] = [];

  for (const [sessionId, session] of sessions) {
    if (now.getTime() - session.createdAt.getTime() > maxAgeMs) {
      expiredSessions.push(sessionId);
    }
  }

  for (const sessionId of expiredSessions) {
    const session = sessions.get(sessionId);
    if (session) {
      try {
        await session.cleanup();
        sessions.delete(sessionId);
        console.error(`Cleaned up expired session: ${sessionId}`);
      } catch (error) {
        console.error(`Error cleaning up expired session ${sessionId}:`, error);
      }
    }
  }
}

/**
 * Get session clients for a specific session ID (backwards compatibility)
 */
export function getSessionClients(
  sessionId: string,
  sessions: Map<string, DatabaseSession>
): DatabaseClients | null {
  const session = sessions.get(sessionId);
  return session ? session.clients : null;
}
