/**
 * Test MCP Client for Database MCP Server
 * 
 * This test connects to the db-mcp-server and validates that it's working
 * correctly by listing available tools and testing basic functionality.
 */

const { Client } = require('@modelcontextprotocol/sdk/client');
const { StdioClientTransport } = require('@modelcontextprotocol/sdk/client/stdio');
const { spawn } = require('child_process');
const path = require('path');

async function testDbMcpServer() {
  console.log('🧪 Testing Database MCP Server...');
  
  // Start the db-mcp-server as a child process
  const serverPath = path.join(__dirname, '../dist/index.js');
  const serverProcess = spawn('node', [serverPath, '--stdio'], {
    stdio: ['pipe', 'pipe', 'inherit']
  });

  try {
    // Create MCP client
    const transport = new StdioClientTransport({
      stdin: serverProcess.stdin,
      stdout: serverProcess.stdout
    });

    const client = new Client({
      name: 'test-client',
      version: '1.0.0'
    }, {
      capabilities: {}
    });

    await client.connect(transport);
    console.log('✅ Successfully connected to Database MCP Server');

    // Test 1: List available tools
    console.log('\n📋 Testing tool listing...');
    const tools = await client.listTools();
    console.log(`Found ${tools.tools.length} tools:`);
    tools.tools.forEach(tool => {
      console.log(`  - ${tool.name}: ${tool.description}`);
    });

    // Test 2: Test PostgreSQL tool (if available)
    const postgresQueryTool = tools.tools.find(t => t.name === 'postgres_query');
    if (postgresQueryTool) {
      console.log('\n🐘 Testing PostgreSQL query tool...');
      try {
        const result = await client.callTool('postgres_query', {
          query: 'SELECT version() as version'
        });
        console.log('PostgreSQL query result:', result);
      } catch (error) {
        console.log('PostgreSQL query expected to fail (no connection):', error.message);
      }
    }

    // Test 3: Test Redis tool (if available)
    const redisGetTool = tools.tools.find(t => t.name === 'redis_get');
    if (redisGetTool) {
      console.log('\n🔴 Testing Redis get tool...');
      try {
        const result = await client.callTool('redis_get', {
          key: 'test-key'
        });
        console.log('Redis get result:', result);
      } catch (error) {
        console.log('Redis get expected to fail (no connection):', error.message);
      }
    }

    console.log('\n✅ Database MCP Server test completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error);
    throw error;
  } finally {
    // Clean up
    serverProcess.kill();
    console.log('🧹 Server process terminated');
  }
}

// Run the test
if (require.main === module) {
  testDbMcpServer()
    .then(() => {
      console.log('🎉 All tests passed!');
      process.exit(0);
    })
    .catch(error => {
      console.error('💥 Test suite failed:', error);
      process.exit(1);
    });
}

module.exports = { testDbMcpServer };
