/**
 * Simple Test for Database MCP Server
 * 
 * This test validates that the server builds and initializes correctly.
 */

import { createServer, config, serverConfig } from '../dist/index.js';

async function testDbMcpServer() {
  console.log('🧪 Testing Database MCP Server initialization...');
  
  try {
    console.log('📋 Server configuration:');
    console.log(`  Name: ${serverConfig.serverName}`);
    console.log(`  Version: ${serverConfig.serverVersion}`);
    console.log(`  PostgreSQL enabled: ${config.postgres.enabled}`);
    console.log(`  Redis enabled: ${config.redis?.enabled || false}`);
    console.log(`  MongoDB enabled: ${config.mongodb?.enabled || false}`);
    console.log(`  InfluxDB enabled: ${config.influxdb?.enabled || false}`);

    console.log('\n🔧 Creating server instance...');
    const server = createServer();
    
    if (server) {
      console.log('✅ Server instance created successfully');
      console.log('🛠️  Server name:', server.name);
      console.log('📦 Server version:', server.version);
    } else {
      throw new Error('Failed to create server instance');
    }

    console.log('\n✅ Database MCP Server test completed successfully!');
    return true;

  } catch (error) {
    console.error('❌ Test failed:', error);
    throw error;
  }
}

// Run the test
testDbMcpServer()
  .then(() => {
    console.log('🎉 All tests passed!');
    process.exit(0);
  })
  .catch(error => {
    console.error('💥 Test suite failed:', error);
    process.exit(1);
  });
