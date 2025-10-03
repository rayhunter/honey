# OMDB MCP Server - Testing Guide

## 🚀 Comprehensive MCP Testing Methods

This guide provides multiple approaches for testing the OMDB MCP Server, which implements the Model Context Protocol (MCP) using Spring AI's HTTP JSON-RPC transport. These methods offer reliable alternatives to MCP Inspector with full compatibility for HTTP-based MCP implementations.

### ✅ **1. Direct HTTP JSON-RPC Testing (Recommended)**

The most reliable method for testing the OMDB MCP Server:

```bash
# Test tools list
curl -X POST "http://localhost:8081/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'

# Test movie search
curl -X POST "http://localhost:8081/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": 2, 
    "method": "tools/call", 
    "params": {
      "name": "search_movies", 
      "arguments": {"title": "Matrix"}
    }
  }'

# Test movie details by title
curl -X POST "http://localhost:8081/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": 3, 
    "method": "tools/call", 
    "params": {
      "name": "get_movie_details", 
      "arguments": {"title": "The Matrix", "year": "1999"}
    }
  }'

# Test movie details by IMDB ID
curl -X POST "http://localhost:8081/mcp" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0", 
    "id": 4, 
    "method": "tools/call", 
    "params": {
      "name": "get_movie_by_imdb_id", 
      "arguments": {"imdbId": "tt0133093"}
    }
  }'
```

### ✅ **2. Python MCP SDK Client (Advanced)**

For developers who want to build MCP clients or test the protocol comprehensively:

#### HTTP Client Example
```python
import asyncio
import httpx
import json

async def test_omdb_mcp_server():
    """Test OMDB MCP Server using direct HTTP calls"""
    async with httpx.AsyncClient() as client:
        # Test tools list
        response = await client.post(
            "http://localhost:8081/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        )
        tools_result = response.json()
        print("Available tools:", [tool["name"] for tool in tools_result["result"]["tools"]])
        
        # Test movie search
        response = await client.post(
            "http://localhost:8081/mcp",
            json={
                "jsonrpc": "2.0", 
                "id": 2, 
                "method": "tools/call",
                "params": {
                    "name": "search_movies",
                    "arguments": {"title": "Matrix"}
                }
            }
        )
        search_result = response.json()
        print("Search result:", search_result["result"])

# Run the test
asyncio.run(test_omdb_mcp_server())
```

#### Using MCP Python SDK (For Reference)
```python
# Note: The official MCP Python SDK is designed for STDIO transport
# For HTTP-based MCP servers like this one, direct HTTP calls are recommended
# This example shows the concept for educational purposes

from mcp.client.session import ClientSession
import asyncio

# This would require a custom HTTP transport implementation
# The OMDB MCP Server uses HTTP JSON-RPC, not the SDK's expected transports
```

### ✅ **3. Automated Testing Scripts**

Create reusable test scripts for continuous integration:

#### Bash Test Script
```bash
#!/bin/bash
# test-mcp-server.sh

SERVER_URL="http://localhost:8081/mcp"
SUCCESS=0
FAILED=0

test_endpoint() {
    local name="$1"
    local payload="$2"
    
    echo "Testing: $name"
    response=$(curl -s -X POST "$SERVER_URL" \
        -H "Content-Type: application/json" \
        -d "$payload")
    
    if echo "$response" | jq -e '.result' > /dev/null 2>&1; then
        echo "✅ $name - PASSED"
        ((SUCCESS++))
    else
        echo "❌ $name - FAILED"
        echo "Response: $response"
        ((FAILED++))
    fi
    echo
}

# Test cases
test_endpoint "List Tools" \
    '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

test_endpoint "Search Movies" \
    '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_movies","arguments":{"title":"Matrix"}}}'

test_endpoint "Get Movie Details" \
    '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_movie_details","arguments":{"title":"The Matrix","year":"1999"}}}'

test_endpoint "Get Movie by IMDB ID" \
    '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"get_movie_by_imdb_id","arguments":{"imdbId":"tt0133093"}}}'

echo "Results: $SUCCESS passed, $FAILED failed"
exit $FAILED
```

### ✅ **4. Browser-Based Testing**

Create a simple HTML page to test the HTTP endpoint interactively:

```html
<!DOCTYPE html>
<html>
<head>
    <title>OMDB MCP Server Tester</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        button { margin: 10px; padding: 10px; }
        pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>OMDB MCP Server Test Interface</h1>
    <button onclick="testTools()">List Tools</button>
    <button onclick="testSearch()">Search Matrix</button>
    <button onclick="testDetails()">Get Matrix Details</button>
    <pre id="result">Click a button to test the MCP server...</pre>
    
    <script>
    async function testTools() {
        const response = await fetch('http://localhost:8081/mcp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                jsonrpc: '2.0', id: 1, method: 'tools/list', params: {}
            })
        });
        document.getElementById('result').textContent = 
            JSON.stringify(await response.json(), null, 2);
    }
    
    async function testSearch() {
        const response = await fetch('http://localhost:8081/mcp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                jsonrpc: '2.0', id: 2, method: 'tools/call',
                params: {name: 'search_movies', arguments: {title: 'Matrix'}}
            })
        });
        document.getElementById('result').textContent = 
            JSON.stringify(await response.json(), null, 2);
    }
    
    async function testDetails() {
        const response = await fetch('http://localhost:8081/mcp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                jsonrpc: '2.0', id: 3, method: 'tools/call',
                params: {name: 'get_movie_details', arguments: {title: 'The Matrix', year: '1999'}}
            })
        });
        document.getElementById('result').textContent = 
            JSON.stringify(await response.json(), null, 2);
    }
    </script>
</body>
</html>
```

### ✅ **5. API Testing Tools (Postman/Insomnia)**

Import this collection for comprehensive API testing:

```json
{
  "info": {"name": "OMDB MCP Server Tests", "description": "Comprehensive test suite for OMDB MCP Server"},
  "item": [
    {
      "name": "List Tools",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\",\"params\":{}}"
        },
        "url": {"raw": "http://localhost:8081/mcp"}
      }
    },
    {
      "name": "Search Movies - Matrix",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{\"name\":\"search_movies\",\"arguments\":{\"title\":\"Matrix\"}}}"
        },
        "url": {"raw": "http://localhost:8081/mcp"}
      }
    },
    {
      "name": "Get Movie Details - The Matrix",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{\"name\":\"get_movie_details\",\"arguments\":{\"title\":\"The Matrix\",\"year\":\"1999\"}}}"
        },
        "url": {"raw": "http://localhost:8081/mcp"}
      }
    },
    {
      "name": "Get Movie by IMDB ID - The Matrix",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"tools/call\",\"params\":{\"name\":\"get_movie_by_imdb_id\",\"arguments\":{\"imdbId\":\"tt0133093\"}}}"
        },
        "url": {"raw": "http://localhost:8081/mcp"}
      }
    }
  ]
}
```

## 🔧 **Troubleshooting**

### Common Issues

#### Connection Refused
**Problem**: `curl: (7) Failed to connect to localhost port 8081`  
**Solution**: Ensure the OMDB MCP Server is running:
```bash
# Check if server is running
curl http://localhost:8081/actuator/health

# If not running, start the server
java -jar target/omdb-mcp-server-*.jar
```

#### Invalid JSON-RPC Request
**Problem**: `{"jsonrpc":"2.0","id":1,"error":{"code":-32600,"message":"Invalid Request"}}`  
**Solution**: Verify your JSON-RPC request format matches the examples above.

#### Tool Not Found Error
**Problem**: `{"jsonrpc":"2.0","id":1,"error":{"code":-32601,"message":"Method not found"}}`  
**Solution**: Use `tools/list` to see available tools, then use `tools/call` with correct tool names.

### MCP Inspector Compatibility

**Note**: This server implements HTTP JSON-RPC transport, which differs from the complex transport protocols expected by MCP Inspector. For reliable testing, use the methods documented above rather than MCP Inspector.

## ✅ **Quick Verification**

Verify the server is working correctly:

```bash
# 1. Check server health
curl http://localhost:8081/actuator/health

# 2. List available tools
curl -X POST "http://localhost:8081/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'

# 3. Test a simple movie search
curl -X POST "http://localhost:8081/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "search_movies", "arguments": {"title": "Matrix"}}}'
```

**Expected Response Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {"name": "search_movies", "description": "Search for movies by title..."},
      {"name": "get_movie_details", "description": "Get detailed information..."},
      {"name": "get_movie_by_imdb_id", "description": "Get detailed movie information..."}
    ]
  }
}
```

## 🛠 **Available Tools**

1. **search_movies** - Search for movies by title with optional year and type filters
2. **get_movie_details** - Get detailed information about a specific movie by title  
3. **get_movie_by_imdb_id** - Get detailed movie information using IMDB ID

All tools include rich JSON schemas with validation, examples, and proper documentation.

## 📡 **Server Configuration**

### Default Settings
- **Port**: 8081
- **HTTP Endpoint**: `/mcp` (JSON-RPC)
- **Health Check**: `/actuator/health`
- **Network Binding**: 0.0.0.0 (all interfaces)
- **CORS**: Enabled for cross-origin requests

### Environment Requirements
- **Java**: 17 or higher
- **OMDB API Key**: Required for movie data access
- **Network Access**: Internet connection for OMDB API calls

### Configuration
Set your OMDB API key:
```bash
export OMDB_API_KEY=your-api-key-here
```

Or configure in `application.properties`:
```properties
omdb.api.key=your-api-key-here
```

## 🎯 **Recommendations by Use Case**

### 🧪 **Development & Testing**
- **Direct HTTP calls** (curl/Postman) - Fastest for API testing and debugging
- **Browser testing** - Visual interface for interactive testing
- **Automated scripts** - For continuous integration and regression testing

### 🔧 **Production Integration** 
- **HTTP JSON-RPC clients** - For custom application integration
- **API testing tools** - For comprehensive endpoint validation
- **Python/JavaScript clients** - For building MCP-aware applications

### 📊 **Debugging & Analysis**
- **Health endpoints** - For monitoring server status
- **Structured logging** - For troubleshooting issues
- **Test automation** - For validating functionality

---

## 🎉 **Conclusion**

The OMDB MCP Server provides a robust HTTP JSON-RPC implementation of the Model Context Protocol, offering reliable movie data access through multiple testing approaches. The methods documented in this guide ensure comprehensive testing coverage for development, integration, and production scenarios.

**Key Takeaways:**
- HTTP JSON-RPC transport provides reliable, scalable MCP implementation
- Multiple testing methods support different development workflows
- Direct HTTP calls offer the most straightforward testing approach
- Comprehensive tool coverage for movie search and details retrieval

For additional information, see the main [README.md](README.md) and explore the server's OpenAPI documentation at `http://localhost:8081/swagger-ui/index.html` when running.

