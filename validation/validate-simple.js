/**
 * Simple validation script for Database MCP Server
 */

import { createServer, config } from '../dist/index.js';

async function validateServer() {
  console.log('🔍 Validating Database MCP Server...');
  
  try {
    console.log('📋 Configuration:');
    console.log(`  PostgreSQL: ${config.postgres.enabled ? '✅' : '❌'}`);
    console.log(`  Redis: ${config.redis?.enabled ? '✅' : '❌'}`);
    console.log(`  MongoDB: ${config.mongodb?.enabled ? '✅' : '❌'}`);
    console.log(`  InfluxDB: ${config.influxdb?.enabled ? '✅' : '❌'}`);

    console.log('\n🔧 Creating server...');
    const server = createServer();
    
    if (server) {
      console.log('✅ Server created successfully');
      console.log('🎉 Database MCP Server validation completed!');
      process.exit(0);
    } else {
      throw new Error('Failed to create server');
    }
  } catch (error) {
    console.error('❌ Validation failed:', error);
    process.exit(1);
  }
}

validateServer();
