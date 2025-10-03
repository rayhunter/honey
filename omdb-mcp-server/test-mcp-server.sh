#!/bin/bash

# Sample script to test the OMDB MCP Server
# Make sure the server is running on localhost:8081

BASE_URL="http://localhost:8081/mcp"

echo "Testing OMDB MCP Server..."
echo "========================="

# Test 1: Initialize
echo -e "\n1. Testing Initialize..."
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "test-client",
        "version": "1.0.0"
      }
    }
  }' | jq .

# Test 2: List Tools
echo -e "\n2. Testing Tools List..."
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/list"
  }' | jq .

# Test 3: Search Movies
echo -e "\n3. Testing Search Movies..."
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "search_movies",
      "arguments": {
        "title": "Matrix"
      }
    }
  }' | jq .

# Test 4: Get Movie Details
echo -e "\n4. Testing Get Movie Details..."
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "4",
    "method": "tools/call",
    "params": {
      "name": "get_movie_details",
      "arguments": {
        "title": "The Matrix",
        "year": "1999"
      }
    }
  }' | jq .

# Test 5: Get Movie by IMDB ID
echo -e "\n5. Testing Get Movie by IMDB ID..."
curl -s -X POST $BASE_URL \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "5",
    "method": "tools/call",
    "params": {
      "name": "get_movie_by_imdb_id",
      "arguments": {
        "imdbId": "tt0133093"
      }
    }
  }' | jq .

echo -e "\nDone!"
