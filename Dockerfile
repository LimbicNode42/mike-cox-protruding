# Use Node.js LTS Alpine for smaller image size
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./
COPY tsconfig.json ./

# Copy source code (needed for build)
COPY src/ ./src/

# Install all dependencies (including dev dependencies for build)
RUN npm ci && npm cache clean --force

# Build the project
RUN npm run build

# Remove dev dependencies to reduce image size
RUN npm ci --only=production && npm cache clean --force

# Remove source files after build
RUN rm -rf src/ tsconfig.json

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S mcp -u 1001 -G nodejs

# Change ownership of the app directory
RUN chown -R mcp:nodejs /app
USER mcp

# Expose port (configurable via environment)
EXPOSE 8000

# Environment variables for server configuration
ENV HOST=0.0.0.0
ENV PORT=8000
ENV NODE_ENV=production
ENV LOG_LEVEL=info
ENV MCP_ALLOWED_HOSTS=""

# PostgreSQL Configuration
ENV ENABLE_POSTGRES=false
ENV POSTGRES_URL=""

# Redis Configuration
ENV ENABLE_REDIS=false
ENV REDIS_URL=""

# MongoDB Configuration
ENV ENABLE_MONGODB=false
ENV MONGODB_URL=""

# InfluxDB Configuration
ENV ENABLE_INFLUXDB=false
ENV INFLUXDB_URL=""
ENV INFLUXDB_TOKEN=""
ENV INFLUXDB_ORG=""
ENV INFLUXDB_BUCKET=""

# MCP Server Security Configuration
ENV MCP_ENABLE_DNS_REBINDING_PROTECTION=false
ENV MCP_ALLOWED_HOSTS=""
ENV API_KEY=""

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "const http = require('http'); const options = { host: process.env.HOST || '0.0.0.0', port: process.env.PORT || 8000, path: '/health', timeout: 2000 }; const req = http.request(options, (res) => { if (res.statusCode === 200) process.exit(0); else process.exit(1); }); req.on('error', () => process.exit(1)); req.end();" || exit 1

# Default command runs in HTTP mode for Docker deployment
CMD ["sh", "-c", "node dist/index.js --mode http --host $HOST --port $PORT"]
