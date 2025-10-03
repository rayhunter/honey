#!/bin/bash

# Test OpenAPI Documentation Integration
# This script validates that the OpenAPI endpoints are accessible

echo "🧪 Testing OpenAPI Documentation Integration"
echo "============================================="

# Start the application in the background
echo "🚀 Starting OMDB MCP Server..."
OMDB_API_KEY=test nohup ./mvnw spring-boot:run -DskipTests > app.log 2>&1 &
APP_PID=$!

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 20

# Function to cleanup
cleanup() {
    echo "🧹 Cleaning up..."
    kill $APP_PID 2>/dev/null
    rm -f app.log nohup.out
    exit $1
}

# Test OpenAPI JSON endpoint
echo "📋 Testing OpenAPI JSON endpoint..."
if curl -s -f http://localhost:8081/v3/api-docs > /dev/null; then
    echo "✅ OpenAPI JSON endpoint is accessible"
else
    echo "❌ OpenAPI JSON endpoint failed"
    cleanup 1
fi

# Test Swagger UI endpoint
echo "🌐 Testing Swagger UI endpoint..."
if curl -s -f http://localhost:8081/swagger-ui/index.html > /dev/null; then
    echo "✅ Swagger UI endpoint is accessible"
else
    echo "❌ Swagger UI endpoint failed"
    cleanup 1
fi

# Test MCP health endpoint
echo "🏥 Testing MCP health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8081/mcp/health)
if [ "$HEALTH_RESPONSE" = "MCP Server is running" ]; then
    echo "✅ MCP health endpoint working correctly"
else
    echo "❌ MCP health endpoint failed. Response: $HEALTH_RESPONSE"
    cleanup 1
fi

# Test cache stats endpoint
echo "📊 Testing cache stats endpoint..."
if curl -s -f http://localhost:8081/cache/stats > /dev/null; then
    echo "✅ Cache stats endpoint is accessible"
else
    echo "❌ Cache stats endpoint failed"
    cleanup 1
fi

echo ""
echo "🎉 All OpenAPI documentation tests passed!"
echo "📖 Access documentation at:"
echo "   - Swagger UI: http://localhost:8081/swagger-ui/index.html"
echo "   - OpenAPI JSON: http://localhost:8081/v3/api-docs"

cleanup 0
