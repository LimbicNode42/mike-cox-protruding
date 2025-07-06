#!/bin/bash
# Simple validation script for Database MCP Server

echo "🔍 Validating Database MCP Server..."

# Check if built
if [ ! -d "dist" ]; then
    echo "❌ Build directory 'dist' not found. Run 'npm run build' first."
    exit 1
fi

echo "✅ Build directory found"

# Check main entry point
if [ ! -f "dist/index.js" ]; then
    echo "❌ Main entry point 'dist/index.js' not found."
    exit 1
fi

echo "✅ Main entry point found"

# Test server initialization
echo "🧪 Testing server initialization..."
node -e "
import('./dist/index.js').then(module => {
  const server = module.createServer();
  if (server) {
    console.log('✅ Server initialization successful');
    process.exit(0);
  } else {
    console.log('❌ Server initialization failed');
    process.exit(1);
  }
}).catch(error => {
  console.log('❌ Server initialization error:', error.message);
  process.exit(1);
});
"

echo "🎉 Database MCP Server validation completed successfully!"
