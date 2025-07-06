/**
 * Test MCP Server Resources
 *
 * This script tests the db-mcp-server resources using the MCP SDK client.
 */

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

async function testResources() {
  console.log('🧪 Testing db-mcp-server resources...');

  const serverPath = resolve(__dirname, '../dist/index.js');
  console.log(`📍 Server path: ${serverPath}`);

  // Create client
  const client = new Client(
    {
      name: 'test-client',
      version: '1.0.0',
    },
    {
      capabilities: {},
    }
  );

  // Create transport
  const transport = new StdioClientTransport({
    command: 'node',
    args: [serverPath, '--mode', 'stdio'],
  });

  try {
    // Connect to server
    console.log('🔌 Connecting to server...');
    await client.connect(transport);
    console.log('✅ Connected to server');

    // List resources
    console.log('\n📚 Listing resources...');
    const resourcesResult = await client.request({
      method: 'resources/list',
      params: {},
    });

    console.log('✅ Resources found:', resourcesResult.resources?.length || 0);
    for (const resource of resourcesResult.resources || []) {
      console.log(`  📄 ${resource.name}: ${resource.uri}`);
    }

    // Test reading each resource
    if (resourcesResult.resources && resourcesResult.resources.length > 0) {
      console.log('\n🔍 Testing resource reads...');

      for (const resource of resourcesResult.resources) {
        try {
          console.log(`\n📖 Reading: ${resource.name}`);
          const readResult = await client.request({
            method: 'resources/read',
            params: {
              uri: resource.uri,
            },
          });

          console.log(`✅ Successfully read ${resource.name}`);
          if (readResult.contents && readResult.contents[0]) {
            const content = readResult.contents[0];
            console.log(`   📄 Content type: ${content.mimeType}`);
            console.log(`   📏 Content length: ${content.text?.length || 0} chars`);

            // Parse JSON content for preview
            if (content.mimeType === 'application/json' && content.text) {
              try {
                const jsonData = JSON.parse(content.text);
                console.log(`   🔍 Preview:`, Object.keys(jsonData).slice(0, 5));
              } catch (e) {
                console.log(`   ⚠️  Could not parse JSON content`);
              }
            }
          }
        } catch (error) {
          console.error(`❌ Failed to read ${resource.name}:`, error.message);
        }
      }
    }

    console.log('\n✅ Resource test completed successfully!');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  } finally {
    // Clean up
    try {
      await client.close();
    } catch (e) {
      // Ignore cleanup errors
    }
  }
}

// Run the test
testResources().catch(error => {
  console.error('❌ Test error:', error);
  process.exit(1);
});
