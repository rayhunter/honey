#!/bin/bash

# Test SSE MCP connection and tools list
echo "Testing Spring AI MCP Server SSE Transport..."

# Start SSE connection in background and capture session ID
echo "1. Establishing SSE connection..."
SSE_OUTPUT=$(curl -s -N -H "Accept: text/event-stream" "http://localhost:8081/sse" --max-time 3 | head -1)
echo "SSE Response: $SSE_OUTPUT"

# Extract session ID from the response
SESSION_ID=$(echo "$SSE_OUTPUT" | grep -o 'sessionId=[^"]*' | cut -d'=' -f2)
echo "Session ID: $SESSION_ID"

if [ -z "$SESSION_ID" ]; then
    echo "Failed to get session ID from SSE endpoint"
    exit 1
fi

# Test tools/list
echo -e "\n2. Testing tools/list..."
curl -s -X POST "http://localhost:8081/mcp/message?sessionId=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list"
  }' | jq '.' 2>/dev/null || curl -s -X POST "http://localhost:8081/mcp/message?sessionId=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": "1",
    "method": "tools/list"
  }'

echo -e "\n3. Testing search_movies tool..."
curl -s -X POST "http://localhost:8081/mcp/message?sessionId=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2", 
    "method": "tools/call",
    "params": {
      "name": "search_movies",
      "arguments": {
        "title": "Inception"
      }
    }
  }' | jq '.' 2>/dev/null || curl -s -X POST "http://localhost:8081/mcp/message?sessionId=$SESSION_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call", 
    "params": {
      "name": "search_movies",
      "arguments": {
        "title": "Inception"
      }
    }
  }'

echo -e "\n\nSSE MCP Test completed."
