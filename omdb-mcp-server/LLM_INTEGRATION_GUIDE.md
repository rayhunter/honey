# OMDB MCP Server - LLM Integration Guide

This guide explains how to integrate the OMDB MCP Server with Large Language Models (LLMs) to enable AI assistants to search for movies and retrieve detailed movie information from the Open Movie Database (OMDB).

The OMDB MCP Server is built with **Spring AI's native MCP Server support**, implementing the Model Context Protocol (MCP) 2024-11-05 specification for seamless integration with AI assistants and LLM clients.

## Table of Contents

1. [Understanding the Architecture](#understanding-the-architecture)
2. [Prerequisites](#prerequisites)
3. [Setting Up the MCP Server](#setting-up-the-mcp-server)
4. [MCP Client Integration](#mcp-client-integration)
5. [Testing with Ollama](#testing-with-ollama)
6. [Tool Usage Patterns](#tool-usage-patterns)
7. [Example Conversations](#example-conversations)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

## Understanding the Architecture

### Spring AI MCP Server

Spring AI provides native MCP Server support with autoconfiguration and Function-based tool registration. The OMDB MCP Server leverages these capabilities:

```
┌─────────────────┐   SSE    ┌──────────────────┐    ┌─────────────────┐
│   LLM Client    │─────────▶│  Spring AI MCP   │───▶│   OMDB API      │
│  (AI Assistant) │   /sse   │     Server       │    │ (omdbapi.com)   │
└─────────────────┘          └──────────────────┘    └─────────────────┘
        │                           │                       │
        │                           ▼                       │
        │                   ┌──────────────────┐            │
        │                   │ Function Beans   │            │
        │                   │   (MCP Tools)    │            │
        │                   └──────────────────┘            │
        │                           │                       │
        │                           ▼                       │
        │                   ┌──────────────────┐            │
        └──────────────────▶│  Cached Results  │◀───────────┘
                            │  (In Memory)     │
                            └──────────────────┘
```

### Key Components

- **Spring AI MCP Autoconfiguration**: Automatic server setup and protocol handling
- **Function Beans**: Tools registered as Spring Function components for auto-discovery
- **SSE Transport**: Server-Sent Events at `/sse` for real-time bidirectional communication
- **WebFlux Integration**: Reactive architecture for scalable performance

### Available Tools

The server provides three main tools to LLMs:

1. **`search_movies`** - Search for movies by title, year, and type
2. **`get_movie_details`** - Get detailed information about a specific movie
3. **`get_movie_by_imdb_id`** - Retrieve movie details using IMDB ID

## Prerequisites

### For the MCP Server

- Java 23 or higher
- OMDB API Key (free from http://www.omdbapi.com/apikey.aspx)
- Docker (optional, for containerized deployment)

### For LLM Integration

- An LLM client that supports MCP (e.g., Claude Desktop, OpenAI ChatGPT with plugins, custom clients)
- Network access to the MCP server
- Basic understanding of JSON-RPC 2.0 protocol

## Setting Up the MCP Server

### Option 1: Docker (Recommended)

```bash
# Pull and run the latest Docker image
docker run -d \
  --name omdb-mcp-server \
  -p 8081:8081 \
  -e OMDB_API_KEY=your-actual-api-key-here \
  ghcr.io/tyrell/omdb-mcp-server:latest
```

### Option 2: Pre-built JAR

```bash
# Download the latest JAR from GitHub Releases
wget https://github.com/tyrell/omdb-mcp-server/releases/latest/download/omdb-mcp-server.jar

# Run with your API key
java -jar omdb-mcp-server.jar --omdb.api.key=your-actual-api-key-here
```

### Option 3: Build from Source

```bash
# Clone and build
git clone https://github.com/tyrell/omdb-mcp-server
cd omdb-mcp-server
./mvnw clean package

# Set API key and run
export OMDB_API_KEY=your-actual-api-key-here
./mvnw spring-boot:run
```

### Verify Installation

Once running, verify the server is working:

```bash
# Health check
curl http://localhost:8081/actuator/health

# Check Spring AI MCP server info
curl http://localhost:8081/actuator/info

# Test SSE endpoint (should establish connection)
curl -N -H "Accept: text/event-stream" http://localhost:8081/sse

# View API documentation
open http://localhost:8081/swagger-ui/index.html
```

## MCP Client Integration

### Configuration for Claude Desktop

Add this configuration to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "omdb": {
      "command": "java",
      "args": [
        "-jar", 
        "/path/to/omdb-mcp-server.jar"
      ],
      "env": {
        "OMDB_API_KEY": "your-actual-api-key-here",
        "SERVER_PORT": "8081"
      }
    }
  }
}
```

### Configuration for Custom MCP Clients

For custom implementations, connect to the Spring AI MCP server using Server-Sent Events:

**SSE Endpoint**: `http://localhost:8081/sse`  
**Protocol**: MCP 2024-11-05 over Server-Sent Events  
**Content-Type**: `text/event-stream`

#### JavaScript/TypeScript Example

```javascript
// Establish SSE connection to Spring AI MCP Server
const eventSource = new EventSource('http://localhost:8081/sse');

eventSource.onopen = function(event) {
    console.log('Connected to Spring AI MCP Server');
};

eventSource.onmessage = function(event) {
    const mcpMessage = JSON.parse(event.data);
    console.log('Received MCP message:', mcpMessage);
    
    // Handle MCP protocol messages
    switch(mcpMessage.method) {
        case 'initialize':
            // Handle initialization
            break;
        case 'tools/list':
            // Handle tool listing
            break;
        case 'tools/call':
            // Handle tool execution
            break;
    }
};

eventSource.onerror = function(event) {
    console.error('SSE connection error:', event);
};
```

## Testing with Ollama

[Ollama](https://ollama.ai/) is a popular tool for running large language models locally. While Ollama doesn't natively support MCP, you can test the OMDB MCP Server with Ollama through several approaches:

### Approach 1: Custom MCP Client Bridge

Create a simple bridge application that connects Ollama to the MCP server:

#### Python Bridge Example

```python
#!/usr/bin/env python3
"""
Ollama MCP Bridge - Connect Ollama to OMDB MCP Server
"""
import requests
import json
import asyncio
from typing import Dict, Any

class OllamaMcpBridge:
    def __init__(self, 
                 ollama_url: str = "http://localhost:11434",
                 mcp_server_url: str = "http://localhost:8081/sse",
                 model: str = "llama2"):
        self.ollama_url = ollama_url
        self.mcp_server_url = mcp_server_url
        self.model = model
        self.request_id = 0
        
    def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call MCP server tool via MCP protocol"""
        self.request_id += 1
        
        # Create MCP tool call request
        mcp_request = {
            "jsonrpc": "2.0",
            "id": str(self.request_id),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = requests.post(
                "http://localhost:8081/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            mcp_response = response.json()
            if "result" in mcp_response and "content" in mcp_response["result"]:
                # Extract text content from MCP response
                content_items = mcp_response["result"]["content"]
                if content_items and len(content_items) > 0:
                    return content_items[0].get("text", "No content available")
            
            return f"Error: {mcp_response.get('error', 'Unknown MCP error')}"
        except requests.RequestException as e:
            return f"Error calling {tool_name}: {str(e)}"
    
    def process_with_ollama(self, user_query: str) -> str:
        """Process query with Ollama and handle tool calls"""
        
        # System prompt that teaches Ollama about available tools
        system_prompt = """You are an AI assistant with access to movie database tools. 
You can search for movies and get detailed information. Available tools:

1. searchMovies(title, year=optional, type=optional) - Search for movies by title
2. getMovieDetails(title, year=optional, plot=optional) - Get detailed movie information  
3. getMovieByImdbId(imdbId, plot=optional) - Get movie by IMDB ID

When you need movie information, respond with: TOOL_CALL: toolName(param1=value1, param2=value2)
Then I will execute the tool and provide the result."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        # Call Ollama
        response = requests.post(
            f"{self.ollama_url}/api/chat",
            json={
                "model": self.model,
                "messages": messages,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            return f"Error calling Ollama: {response.text}"
            
        ollama_response = response.json()["message"]["content"]
        
        # Check if Ollama wants to call a tool
        if "TOOL_CALL:" in ollama_response:
            tool_call = ollama_response.split("TOOL_CALL:")[1].strip()
            tool_result = self._parse_and_execute_tool_call(tool_call)
            
            # Send tool result back to Ollama
            messages.append({"role": "assistant", "content": ollama_response})
            messages.append({"role": "user", "content": f"Tool result: {tool_result}"})
            
            final_response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False
                }
            )
            
            return final_response.json()["message"]["content"]
        
        return ollama_response
    
    def _parse_and_execute_tool_call(self, tool_call: str) -> str:
        """Parse tool call string and execute the appropriate MCP tool"""
        try:
            # Simple parsing for toolName(param1=value1, param2=value2)
            tool_name = tool_call.split("(")[0].strip()
            params_str = tool_call.split("(")[1].rstrip(")")
            
            arguments = {}
            if params_str:
                for param in params_str.split(","):
                    key, value = param.split("=")
                    arguments[key.strip()] = value.strip().strip("'\"")
            
            return self.call_mcp_tool(tool_name, arguments)
        except Exception as e:
            return f"Error parsing tool call: {str(e)}"

# Usage example
def main():
    bridge = OllamaMcpBridge(model="llama2")  # or "mistral", "codellama", etc.
    
    print("Ollama MCP Bridge - OMDB Movie Search")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("Ask about movies: ")
        if user_input.lower() == 'quit':
            break
            
        response = bridge.process_with_ollama(user_input)
        print(f"\nResponse: {response}\n")

if __name__ == "__main__":
    main()
```

#### Setup Instructions

1. **Install Ollama**: Follow instructions at [ollama.ai](https://ollama.ai/)

2. **Pull a model**:
   ```bash
   ollama pull llama2
   # or
   ollama pull mistral
   # or 
   ollama pull codellama
   ```

3. **Start the OMDB MCP Server**:
   ```bash
   export OMDB_API_KEY=your-api-key-here
   java -jar omdb-mcp-server.jar
   ```

4. **Run the bridge script**:
   ```bash
   pip install requests
   python ollama_mcp_bridge.py
   ```

### Approach 2: Direct MCP Protocol Testing

You can also test the MCP server functionality directly by calling the MCP protocol and then using Ollama to process the results:

```bash
#!/bin/bash
# Test script for Ollama + OMDB MCP integration

# Function to call MCP server and get Ollama analysis
test_movie_with_ollama() {
    local movie_title="$1"
    local year="$2"
    
    echo "🎬 Searching for: $movie_title ($year)"
    
    # Create MCP request for movie details
    mcp_request=$(cat <<EOF
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "get_movie_details",
    "arguments": {
      "title": "$movie_title",
      "year": "$year"
    }
  }
}
EOF
)
    
    # Get movie data from MCP server
    mcp_response=$(curl -s -X POST "http://localhost:8081/mcp" \
        -H "Content-Type: application/json" \
        -d "$mcp_request")
    
    # Extract movie data from MCP response
    movie_data=$(echo "$mcp_response" | jq -r '.result.content[0].text // "No movie data available"')
    
    # Create prompt for Ollama
    prompt="Analyze this movie data and provide a brief, engaging summary:\n\n${movie_data}\n\nProvide: 1) A concise plot summary, 2) Notable cast and director, 3) Critical reception, 4) Why someone might want to watch it."
    
    # Send to Ollama for analysis
    ollama_response=$(curl -s http://localhost:11434/api/generate \
        -d "{
            \"model\": \"llama2\",
            \"prompt\": \"$prompt\",
            \"stream\": false
        }" | jq -r '.response')
    
    echo "🤖 Ollama Analysis:"
    echo "$ollama_response"
    echo ""
}

# Test with different movies
test_movie_with_ollama "The Matrix" "1999"
test_movie_with_ollama "Inception" "2010"
test_movie_with_ollama "Parasite" "2019"
```

### Approach 3: Ollama Function Calling (Advanced)

Some newer Ollama models support function calling. Here's an example using a function calling capable model:

```python
import requests
import json

def test_ollama_function_calling():
    """Test with Ollama models that support function calling"""
    
    # Define available functions for Ollama
    functions = [
        {
            "name": "search_movies",
            "description": "Search for movies by title, year, and type",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Movie title to search for"},
                    "year": {"type": "string", "description": "Release year (optional)"},
                    "type": {"type": "string", "description": "Type: movie, series, or episode (optional)"}
                },
                "required": ["title"]
            }
        },
        {
            "name": "get_movie_details", 
            "description": "Get detailed information about a specific movie",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Movie title"},
                    "year": {"type": "string", "description": "Release year (optional)"},
                    "plot": {"type": "string", "description": "Plot length: short or full (optional)"}
                },
                "required": ["title"]
            }
        }
    ]
    
    # Chat with function calling
    messages = [
        {
            "role": "system", 
            "content": "You are a movie expert assistant. Use the available functions to search for and retrieve movie information when users ask about films."
        },
        {
            "role": "user",
            "content": "Tell me about the movie Dune from 2021"
        }
    ]
    
    # Call Ollama with function definitions (requires compatible model)
    response = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "mistral",  # or another function-calling capable model
            "messages": messages,
            "functions": functions,
            "stream": False
        }
    )
    
    return response.json()

# Usage
if __name__ == "__main__":
    result = test_ollama_function_calling()
    print(json.dumps(result, indent=2))
```

### Prerequisites for Ollama Testing

1. **Ollama Installation**: 
   ```bash
   # macOS
   brew install ollama
   
   # Or download from https://ollama.ai/
   ```

2. **Start Ollama service**:
   ```bash
   ollama serve
   ```

3. **Pull a compatible model**:
   ```bash
   # For general chat and bridge approach
   ollama pull llama2
   ollama pull mistral
   
   # For function calling (if supported)
   ollama pull mistral:latest
   ```

4. **OMDB MCP Server running**:
   ```bash
   export OMDB_API_KEY=your-api-key-here
   java -jar omdb-mcp-server.jar
   ```

### Testing Workflow

1. **Start both servers**:
   ```bash
   # Terminal 1: Start OMDB MCP Server
   export OMDB_API_KEY=your-api-key-here
   java -jar omdb-mcp-server.jar
   
   # Terminal 2: Start Ollama
   ollama serve
   ```

2. **Test the bridge**:
   ```bash
   python ollama_mcp_bridge.py
   ```

3. **Example conversation**:
   ```
   Ask about movies: What can you tell me about The Matrix from 1999?
   
   Response: TOOL_CALL: getMovieDetails(title=The Matrix, year=1999)
   
   [Bridge executes tool call...]
   
   Final Response: The Matrix (1999) is a groundbreaking science fiction film 
   directed by the Wachowski sisters. It stars Keanu Reeves as Neo, a computer 
   programmer who discovers that reality as he knows it is actually a simulated 
   world created by machines...
   ```

### Benefits of Ollama + MCP Integration

- **Local Processing**: Run LLMs completely locally while accessing external data
- **Privacy**: No data sent to external LLM services
- **Customization**: Fine-tune models for movie-specific tasks
- **Cost Effective**: No API costs for LLM inference
- **Offline Capable**: Works without internet (except for OMDB API calls)

### Limitations and Considerations

- **Manual Integration**: Requires custom bridge code since Ollama doesn't natively support MCP
- **Model Capabilities**: Function calling support varies by model
- **Performance**: Local models may be slower than cloud-based solutions
- **Context Management**: Need to handle conversation state manually
- **Tool Calling**: Limited compared to specialized MCP clients like Claude Desktop

This approach is particularly useful for developers who want to:
- Test MCP servers with local models
- Build custom movie recommendation systems
- Create offline-capable movie chatbots
- Prototype MCP integrations before deploying to production

## Tool Usage Patterns

### 1. Spring AI MCP Automatic Tool Discovery

Spring AI MCP Server automatically handles protocol initialization and tool discovery through Function bean registration. The server exposes three tools as registered Function beans:

- `searchMovies`: Search for movies by title and optional year
- `getMovieDetails`: Get detailed information about a specific movie  
- `getMovieByImdbId`: Retrieve movie information using IMDB ID

### 2. Function Bean Registration

Tools are automatically registered via Spring configuration:

```java
@Configuration
public class McpServerConfig {
    
    @Bean
    public Function<SearchMoviesRequest, String> searchMovies(MovieSearchTools movieSearchTools) {
        return movieSearchTools::searchMovies;
    }
    
    @Bean  
    public Function<GetMovieDetailsRequest, String> getMovieDetails(MovieSearchTools movieSearchTools) {
        return movieSearchTools::getMovieDetails;
    }
    
    @Bean
    public Function<GetMovieByImdbIdRequest, String> getMovieByImdbId(MovieSearchTools movieSearchTools) {
        return movieSearchTools::getMovieByImdbId;
    }
}
```

### 3. Tool Discovery (Handled by Spring AI)

Spring AI automatically handles tool discovery requests from MCP clients. When a client requests available tools, Spring AI responds with the registered Function beans and their schemas.

This returns a list of all available tools with their schemas and descriptions.

### 4. Search for Movies

```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "search_movies",
    "arguments": {
      "title": "Matrix",
      "year": "1999",
      "type": "movie"
    }
  }
}
```

**Parameters:**
- `title` (required): Movie title to search for
- `year` (optional): Year of release
- `type` (optional): "movie", "series", or "episode"

### 5. Get Detailed Movie Information

```json
{
  "jsonrpc": "2.0",
  "id": "4",
  "method": "tools/call",
  "params": {
    "name": "get_movie_details",
    "arguments": {
      "title": "The Matrix",
      "year": "1999",
      "plot": "full"
    }
  }
}
```

**Parameters:**
- `title` (required): Movie title
- `year` (optional): Year of release
- `plot` (optional): "short" or "full" (default: "full")

### 6. Get Movie by IMDB ID

```json
{
  "jsonrpc": "2.0",
  "id": "5",
  "method": "tools/call",
  "params": {
    "name": "get_movie_by_imdb_id",
    "arguments": {
      "imdbId": "tt0133093",
      "plot": "full"
    }
  }
}
```

**Parameters:**
- `imdbId` (required): IMDB ID (e.g., "tt0133093")
- `plot` (optional): "short" or "full" (default: "full")

## Example Conversations

### Conversation 1: Movie Recommendation

**User:** "Can you help me find some good sci-fi movies from the 1990s?"

**LLM Process:**
1. Use `search_movies` with title "sci-fi" or search for specific known titles
2. Use `get_movie_details` for promising results
3. Present formatted recommendations

**Example LLM calls:**
```json
[
  {
    "method": "tools/call",
    "params": {
      "name": "search_movies",
      "arguments": {"title": "Matrix", "year": "1999"}
    }
  },
  {
    "method": "tools/call",
    "params": {
      "name": "get_movie_details",
      "arguments": {"title": "The Matrix", "year": "1999"}
    }
  }
]
```

### Conversation 2: Movie Information Lookup

**User:** "Tell me about the movie with IMDB ID tt0111161"

**LLM Process:**
1. Use `get_movie_by_imdb_id` with the provided IMDB ID
2. Format and present the detailed information

**LLM call:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_movie_by_imdb_id",
    "arguments": {"imdbId": "tt0111161"}
  }
}
```

### Conversation 3: Comparative Analysis

**User:** "Compare the ratings and reviews of The Godfather and The Godfather Part II"

**LLM Process:**
1. Use `get_movie_details` for "The Godfather"
2. Use `get_movie_details` for "The Godfather Part II"
3. Compare and contrast the information

## Best Practices

### For Spring AI MCP Integration

1. **SSE Connection Management**: Maintain persistent SSE connections for optimal performance
   ```javascript
   // Handle connection drops and reconnect
   eventSource.onerror = function(event) {
       console.error('SSE connection lost, reconnecting...');
       setTimeout(() => {
           eventSource = new EventSource('http://localhost:8081/sse');
       }, 5000);
   };
   ```

2. **Function Bean Configuration**: Ensure proper typing for Function beans
   ```java
   // Use strongly-typed request/response records
   @Bean
   public Function<SearchMoviesRequest, String> searchMovies(MovieSearchTools tools) {
       return tools::searchMovies;
   }
   ```

3. **Spring AI Autoconfiguration**: Leverage Spring AI's MCP autoconfiguration
   ```properties
   # Enable Spring AI MCP server
   spring.ai.mcp.server.enabled=true
   spring.ai.mcp.server.type=ASYNC
   spring.ai.mcp.server.transport.type=SSE
   ```

### For LLM Developers

1. **Error Handling**: Always check for error responses and handle them gracefully
   ```json
   {
     "jsonrpc": "2.0",
     "id": "1",
     "error": {
       "code": -32602,
       "message": "Invalid params",
       "data": null
     }
   }
   ```

2. **Caching Awareness**: The server caches responses automatically, so repeated queries are fast and don't consume additional API credits

3. **Rate Limiting**: While the server handles OMDB API rate limits, be mindful of making excessive requests

4. **Search Strategy**: 
   - Start with broad searches using `searchMovies`
   - Use specific details with `getMovieDetails` for exact matches
   - Use `getMovieByImdbId` when you have the exact IMDB ID

### For End Users

1. **Be Specific**: More specific movie titles and years yield better results
2. **Use Context**: Mention directors, actors, or plot details to help disambiguation
3. **Year Information**: Including the release year greatly improves accuracy

### Performance Optimization

1. **Leverage Caching**: Identical requests are served from cache instantly
2. **Monitor Cache Performance**: Use `/cache/stats` endpoint to check hit rates
3. **Clear Cache When Needed**: Use `/cache/clear` for testing or debugging

```bash
# Check cache performance
curl http://localhost:8081/cache/stats

# Clear all caches
curl -X DELETE http://localhost:8081/cache/clear
```

## Error Handling

### Common Error Codes

- **-32700**: Parse error (malformed JSON)
- **-32600**: Invalid request (missing required fields)
- **-32601**: Method not found (unsupported MCP method)
- **-32602**: Invalid params (missing or invalid parameters)
- **-32603**: Internal error (server-side error)

### Example Error Response

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "error": {
    "code": -32602,
    "message": "Title parameter is required",
    "data": null
  }
}
```

### Handling Movie Not Found

When a movie isn't found, the server returns a successful response with an error message in the content:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Movie not found: Movie not found!"
      }
    ]
  }
}
```

## Troubleshooting

### Spring AI MCP Server Issues

1. **Server Won't Start**
   - Check Java version (requires Java 23+)
   - Verify OMDB API key is set correctly
   - Check port 8081 isn't already in use
   - Ensure Spring AI 1.0.0 dependencies are available

2. **SSE Connection Issues**
   - Verify SSE endpoint is accessible: `curl -N -H "Accept: text/event-stream" http://localhost:8081/sse`
   - Check browser/client supports Server-Sent Events
   - Monitor network timeouts and connection drops

3. **Function Bean Registration**
   - Verify Function beans are properly configured in McpServerConfig
   - Check Spring component scanning includes your configuration package
   - Review Spring Boot startup logs for Function bean registration

### API Key Issues

1. **OMDB API Problems**
   - Verify your OMDB API key at http://www.omdbapi.com/
   - Check environment variable is set: `echo $OMDB_API_KEY`
   - For free keys, check daily request limits
   - Monitor server logs for OMDB API responses

### LLM Integration Issues

1. **MCP Connection Issues**
   - Check Spring AI MCP server is running: `curl http://localhost:8081/actuator/health`
   - Verify SSE endpoint responds: `curl -N http://localhost:8081/sse`
   - Check firewall settings and network connectivity

2. **Tool Discovery Problems**
   - Verify Spring AI MCP autoconfiguration is enabled
   - Check Function beans are registered and discoverable
   - Review Spring Boot startup logs for MCP server initialization

3. **Tool Execution Errors**
   - Verify Function bean parameter types match request records
   - Check for proper error handling in Function implementations
   - Monitor Spring AI MCP server logs for execution traces

### Debugging Tips

1. **Enable Debug Logging**
   ```properties
   # Add to application.properties
   logging.level.co.tyrell.omdb_mcp_server=DEBUG
   logging.level.org.springframework.ai.mcp=DEBUG
   logging.level.org.springframework.web.reactive=DEBUG
   ```

2. **Monitor Spring AI MCP Components**
   ```bash
   # Check Spring AI MCP autoconfiguration
   curl http://localhost:8081/actuator/configprops | jq '.contexts.application.beans | with_entries(select(.key | contains("mcp")))'
   
   # Monitor Function bean registration
   curl http://localhost:8081/actuator/beans | jq '.contexts.application.beans | with_entries(select(.key | contains("search") or contains("movie")))'
   ```

3. **Test SSE Connection**
   ```bash
   # Test SSE endpoint manually
   curl -N -H "Accept: text/event-stream" \
        -H "Cache-Control: no-cache" \
        http://localhost:8081/sse
   ```

4. **Monitor Cache Performance**
   ```bash
   curl http://localhost:8081/cache/stats | jq
   ```

## Advanced Configuration

### Custom Port Configuration

```bash
# Change server port
java -jar omdb-mcp-server.jar --server.port=9090
```

### Cache Configuration

```properties
# Extend cache TTL to 2 hours
cache.expire-after-write=2h

# Increase cache size
cache.maximum-size=2000

# Disable cache statistics (for performance)
cache.record-stats=false
```

### Production Deployment

For production use, consider:

1. **Docker Compose Setup**
   ```yaml
   version: '3.8'
   services:
     omdb-mcp-server:
       image: ghcr.io/tyrell/omdb-mcp-server:latest
       ports:
         - "8081:8081"
       environment:
         - OMDB_API_KEY=${OMDB_API_KEY}
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8081/actuator/health"]
         interval: 30s
         timeout: 3s
         retries: 3
   ```

2. **Load Balancing**: Deploy multiple instances behind a load balancer
3. **Monitoring**: Use the provided health checks and metrics endpoints
4. **Security**: Run behind a reverse proxy with proper security headers

## Integration Examples

### Python MCP Client

```python
import requests
import json

class OmdbMcpClient:
    def __init__(self, server_url="http://localhost:8081/mcp"):
        self.server_url = server_url
        self.request_id = 0
    
    def _make_request(self, method, params=None):
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": str(self.request_id),
            "method": method,
            "params": params or {}
        }
        
        response = requests.post(
            self.server_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        return response.json()
    
    def initialize(self):
        return self._make_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "python-client",
                "version": "1.0.0"
            }
        })
    
    def list_tools(self):
        return self._make_request("tools/list")
    
    def search_movies(self, title, year=None, type=None):
        arguments = {"title": title}
        if year:
            arguments["year"] = year
        if type:
            arguments["type"] = type
            
        return self._make_request("tools/call", {
            "name": "search_movies",
            "arguments": arguments
        })

# Usage example
client = OmdbMcpClient()
client.initialize()
result = client.search_movies("Matrix", "1999")
print(result)
```

### Node.js MCP Client

```javascript
const axios = require('axios');

class OmdbMcpClient {
    constructor(serverUrl = 'http://localhost:8081/mcp') {
        this.serverUrl = serverUrl;
        this.requestId = 0;
    }
    
    async makeRequest(method, params = {}) {
        this.requestId++;
        const payload = {
            jsonrpc: '2.0',
            id: this.requestId.toString(),
            method,
            params
        };
        
        const response = await axios.post(this.serverUrl, payload, {
            headers: { 'Content-Type': 'application/json' }
        });
        
        return response.data;
    }
    
    async initialize() {
        return this.makeRequest('initialize', {
            protocolVersion: '2024-11-05',
            capabilities: {},
            clientInfo: {
                name: 'nodejs-client',
                version: '1.0.0'
            }
        });
    }
    
    async searchMovies(title, year = null, type = null) {
        const arguments = { title };
        if (year) arguments.year = year;
        if (type) arguments.type = type;
        
        return this.makeRequest('tools/call', {
            name: 'search_movies',
            arguments
        });
    }
}

// Usage example
(async () => {
    const client = new OmdbMcpClient();
    await client.initialize();
    const result = await client.searchMovies('Matrix', '1999');
    console.log(result);
})();
```

## Conclusion

The OMDB MCP Server provides a robust, cacheable interface for LLMs to access movie information from the OMDB database. By following this guide, you can successfully integrate movie lookup capabilities into your AI assistant, enabling rich conversations about films, movie recommendations, and detailed movie information retrieval.

The server's intelligent caching system ensures optimal performance while respecting API rate limits, making it suitable for both development and production use cases.

For additional support, refer to the project's [GitHub repository](https://github.com/tyrell/omdb-mcp-server) or the comprehensive [API documentation](http://localhost:8081/swagger-ui/index.html) when the server is running.
