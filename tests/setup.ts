// Jest setup file for db-mcp-server tests
import { jest } from '@jest/globals';

// Set up global test timeout
jest.setTimeout(30000);

// Mock environment variables for testing
process.env.NODE_ENV = 'test';
process.env.ENABLE_POSTGRES = 'false';
process.env.ENABLE_REDIS = 'false';
process.env.ENABLE_MONGODB = 'false';
process.env.ENABLE_INFLUXDB = 'false';
