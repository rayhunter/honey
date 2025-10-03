# OMDB MCP Server

[![CI](https://github.com/tyrell/omdb-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/tyrell/omdb-mcp-server/actions/workflows/ci.yml)
[![Build](https://github.com/tyrell/omdb-mcp-server/actions/workflows/build.yml/badge.svg)](https://github.com/tyrell/omdb-mcp-server/actions/workflows/build.yml)
[![Docker](https://github.com/tyrell/omdb-mcp-server/actions/workflows/docker.yml/badge.svg)](https://github.com/tyrell/omdb-mcp-server/actions/workflows/docker.yml)
[![Release](https://github.com/tyrell/omdb-mcp-server/actions/workflows/release.yml/badge.svg)](https://github.com/tyrell/omdb-mcp-server/actions/workflows/release.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Java](https://img.shields.io/badge/Java-24-orange.svg)](https://openjdk.org/projects/jdk/24/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.5.4-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![Spring AI](https://img.shields.io/badge/Spring%20AI-1.0.0-brightgreen.svg)](https://docs.spring.io/spring-ai/reference/)
[![Docker](https://img.shields.io/badge/Docker-Available-blue.svg)](https://github.com/tyrell/omdb-mcp-server/pkgs/container/omdb-mcp-server)
[![MCP](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://spec.modelcontextprotocol.io/specification/)

A Model Context Protocol (MCP) Server powered by **Spring AI** that provides access to the Open Movie Database (OMDB) API. This server uses Spring AI's native MCP Server support to allow AI assistants and other MCP clients to search for movies and retrieve detailed movie information.

## Table of Contents

- [OMDB MCP Server](#omdb-mcp-server)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
    - [🎬 Movie Database Access](#-movie-database-access)
    - [⚡ Intelligent Caching System](#-intelligent-caching-system)
    - [🔌 MCP Protocol Compliance](#-mcp-protocol-compliance)
    - [🚀 Production Ready](#-production-ready)
    - [🔧 Developer Experience](#-developer-experience)
  - [🏗️ Architecture \& Technology Stack](#️-architecture--technology-stack)
    - [Technology Stack](#technology-stack)
    - [Architecture Overview](#architecture-overview)
    - [Key Components](#key-components)
    - [Security Features](#security-features)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
    - [🐳 Using Docker (Recommended)](#-using-docker-recommended)
    - [📦 Using Pre-built JAR](#-using-pre-built-jar)
    - [🔨 Building from Source](#-building-from-source)
  - [🔧 Configuration](#-configuration)
    - [Environment Variables](#environment-variables)
    - [Cache Configuration](#cache-configuration)
    - [Docker Compose](#docker-compose)
    - [Spring AI MCP Server Configuration](#spring-ai-mcp-server-configuration)
  - [MCP Tools](#mcp-tools)
    - [1. search\_movies](#1-search_movies)
    - [2. get\_movie\_details](#2-get_movie_details)
    - [3. get\_movie\_by\_imdb\_id](#3-get_movie_by_imdb_id)
  - [MCP Protocol Implementation](#mcp-protocol-implementation)
    - [Supported Methods](#supported-methods)
    - [Initialize](#initialize)
    - [Ping](#ping)
    - [List Tools](#list-tools)
  - [Configuration](#configuration)
    - [Core Configuration](#core-configuration)
    - [Advanced Configuration](#advanced-configuration)
  - [🧪 Testing \& Validation](#-testing--validation)
    - [Health Check](#health-check)
    - [Cache Performance Testing](#cache-performance-testing)
    - [MCP Protocol Testing](#mcp-protocol-testing)
    - [� Comprehensive Testing Guide](MCP_TESTING_GUIDE.md)
    - [�🔍 Development \& Debugging](#-development--debugging)
  - [🚀 CI/CD \& Deployment](#-cicd--deployment)
    - [Deployment Options](#deployment-options)
  - [📖 OpenAPI Documentation](#-openapi-documentation)
    - [Access Documentation](#access-documentation)
    - [API Endpoints](#api-endpoints)
      - [MCP Protocol Endpoints](#mcp-protocol-endpoints)
      - [Cache Management Endpoints](#cache-management-endpoints)
    - [OpenAPI Specification](#openapi-specification)
    - [Example Usage](#example-usage)
      - [Initialize MCP Connection](#initialize-mcp-connection)
      - [Get Available Tools](#get-available-tools)
      - [Search for Movies](#search-for-movies)
  - [API Response Format](#api-response-format)
  - [Error Handling](#error-handling)
  - [🤝 Contributing](#-contributing)
    - [Development Setup](#development-setup)
    - [Code Style](#code-style)
  - [📄 License](#-license)
  - [🙏 Acknowledgments](#-acknowledgments)
  - [📞 Support](#-support)

## Features

### 🎬 Movie Database Access
- **Search Movies**: Search for movies by title, year, and type
- **Get Movie Details**: Retrieve detailed information about a specific movie by title
- **Get Movie by IMDB ID**: Get detailed information using IMDB ID
- **Rich Metadata**: Access to ratings, cast, plot, awards, and more

### ⚡ Intelligent Caching System
- **Automatic Caching**: All OMDB API responses are automatically cached to reduce API calls
- **Configurable TTL**: Cache entries expire after 1 hour by default (configurable)
- **Memory Efficient**: Maximum cache size of 1000 entries with LRU eviction policy
- **Performance Monitoring**: Built-in cache statistics and management endpoints
- **Rate Limit Protection**: Helps stay within OMDB API usage limits and reduces costs

### 🔌 MCP Protocol Compliance
- **MCP 2024-11-05**: Fully implements the latest MCP specification
- **HTTP JSON-RPC**: Direct HTTP transport optimized for web service integration
- **JSON-RPC 2.0**: Standard protocol with proper error codes (-32700, -32600, -32601, -32602, -32603)
- **Tool Discovery**: Dynamic tool listing with JSON Schema validation
- **Enhanced Schemas**: Rich metadata, validation rules, and examples for better AI understanding
- **Protocol Methods**: Full support for initialize, ping, tools/list, tools/call, and notifications

### 🚀 Production Ready
- **Docker Support**: Multi-platform container images (AMD64/ARM64)
- **Health Checks**: Built-in monitoring and health endpoints
- **Configuration**: Environment-based configuration
- **Logging**: Structured logging with configurable levels
- **Testing**: Comprehensive test suite with coverage reporting

### 🔧 Developer Experience
- **GitHub Actions**: Complete CI/CD pipeline
- **Automated Releases**: Tagged releases with artifacts
- **Security Scanning**: Vulnerability detection and reporting
- **OpenAPI Documentation**: Interactive API documentation with Swagger UI
- **Code Quality**: Automated dependency updates and code analysis

## 🏗️ Architecture & Technology Stack

### Technology Stack
- **☕ Java 24**: Latest Java with modern features and performance improvements  
- **🍃 Spring Boot 3.5.4**: Production-ready application framework
- **🤖 Spring AI 1.0.0**: Native MCP Server support with autoconfiguration
- **⚡ Spring WebFlux**: Reactive programming with SSE transport for MCP communication
- **🗄️ Spring Cache + Caffeine**: High-performance in-memory caching with automatic management
- **🐳 Docker**: Containerized deployment with multi-stage builds
- **🧪 JUnit 5**: Comprehensive testing framework with Spring Boot Test integration
- **📊 JaCoCo**: Code coverage analysis
- **🔒 Spring Security**: Security scanning and best practices

### Architecture Overview
```
                    ┌─────────────────┐
                    │   MCP Client    │
                    │ (Claude Desktop)│
                    └─────────────────┘
                           │
                    ┌──────┴──────┐
                    │             │
           ┌────────▼─────┐ ┌─────▼──────────┐
           │ SSE          │ │ HTTP REST      │
           │ Transport    │ │ Controller     │
           │ (/sse)       │ │ (Port 8081)    │
           └────────┬─────┘ └─────┬──────────┘
                    │             │
                    └──────┬──────┘
                           ▼
                   ┌─────────────────┐
                   │ Spring AI MCP   │
                   │ Autoconfigured  │
                   │ Function Beans  │
                   └─────────────────┘
                           │
                           ▼
                   ┌─────────────────┐
                   │MovieSearchTools │◀─--┐
                   │ (Function Impl) │    │
                   └─────────────────┘    │
                           │              │
                           ▼              │
                   ┌─────────────────┐    │
                   │  OMDB Service   │    │
                   │ (External API)  │    │
                   └─────────────────┘    │
                           │              │
                           ▼              │
┌─────────────────┐ ┌─────────────────┐   │
│ Cache Manager   │ │  Caffeine Cache │   │
│   (Statistics)  │ │  (In-Memory)    │   │
└─────────────────┘ └─────────────────┘   │
        │                     ▲           │
        │                     │           │
        ▼                Cache Miss       │
┌─────────────────┐           │           │
│ Cache Endpoints │           │           │
│ /cache/stats    │           ▼           │
│ /cache/clear    │   ┌─────────────────┐ │
└─────────────────┘   │   OMDB API      │ │
                      │ (omdbapi.com)   │ │
                      └─────────────────┘ │
                           │              │
                           └────────────--┘
                         Cache Hit
```

### Key Components
- **🤖 Spring AI MCP**: Autoconfigured MCP server with WebFlux SSE transport
- **�️ MovieSearchTools**: Service providing OMDB movie search functionality as Spring AI Function beans
- **⚙️ McpServerConfig**: Configuration class registering Function beans for MCP tool discovery
- **🌐 OmdbService**: OMDB API integration with reactive WebClient and intelligent caching
- **⚡ Cache Layer**: Caffeine-based in-memory caching with configurable TTL and LRU eviction
- **📊 Cache Management**: REST endpoints for cache statistics and management (/cache/*)
- **� SSE Transport**: Server-Sent Events endpoint (/sse) for real-time MCP communication
- **📋 Model Classes**: Request/response records for strongly-typed Function interfaces
- **⚙️ Configuration**: Spring AI MCP autoconfiguration via application.properties

### Security Features
- 🔐 Non-root Docker user
- 🛡️ Automated vulnerability scanning
- 🚫 No sensitive data in images
- ✅ Health checks and monitoring
- 🔒 HTTPS support for external APIs

## Prerequisites

- Java 24 or higher
- Maven 3.6 or higher
- OMDB API Key (free registration at http://www.omdbapi.com/apikey.aspx)

## Quick Start

### 🐳 Using Docker (Recommended)

```bash
# Pull and run the latest Docker image
docker run -p 8081:8081 -e OMDB_API_KEY=your-api-key ghcr.io/tyrell/omdb-mcp-server:latest
```

### 📦 Using Pre-built JAR

1. Download the latest JAR from [Releases](https://github.com/tyrell/omdb-mcp-server/releases)
2. Run with your OMDB API key:
   ```bash
   java -jar omdb-mcp-server-*.jar --omdb.api.key=your-api-key
   ```

### 🔨 Building from Source

1. **Clone and build the project**:
   ```bash
   git clone https://github.com/tyrell/omdb-mcp-server
   cd omdb-mcp-server
   ./mvnw clean package
   ```

2. **Set your OMDB API key**:
   ```bash
   export OMDB_API_KEY=your-actual-api-key-here
   ```

3. **Run the server**:
   ```bash
   ./mvnw spring-boot:run
   ```

The server will start on `http://localhost:8081`

**📖 View API Documentation**: Once running, access the interactive API documentation at http://localhost:8081/swagger-ui/index.html

## 🔧 Configuration

### Environment Variables
- `OMDB_API_KEY`: Your OMDB API key (required)
- `SERVER_PORT`: Server port (default: 8081)
- `SPRING_AI_MCP_SERVER_NAME`: MCP server name (default: "OMDB Movie Database Server")
- `SPRING_AI_MCP_SERVER_VERSION`: MCP server version (default: "0.2.0-SNAPSHOT")

### Cache Configuration
The server includes intelligent caching to reduce OMDB API calls:

```properties
# Cache Configuration (default values shown)
cache.expire-after-write=1h        # Cache TTL (Time To Live)
cache.maximum-size=1000           # Maximum number of cached entries
cache.record-stats=true           # Enable cache statistics
```

Cache management endpoints:
- `GET /cache/stats` - View cache performance statistics
- `DELETE /cache/clear` - Clear all caches
- `DELETE /cache/clear/{cacheName}` - Clear specific cache

### Docker Compose
```yaml
version: '3.8'
services:
  omdb-mcp-server:
    image: ghcr.io/tyrell/omdb-mcp-server:latest
    ports:
      - "8081:8081"
    environment:
      - OMDB_API_KEY=your-api-key-here
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:8081/actuator/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Spring AI MCP Server Configuration

For AI clients like Claude Desktop, use the Server-Sent Events (SSE) transport:

**SSE Endpoint**: `http://localhost:8081/sse`

**Claude Desktop Configuration** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "omdb": {
      "command": "java",
      "args": ["-jar", "/path/to/omdb-mcp-server.jar"],
      "env": {
        "OMDB_API_KEY": "your-actual-api-key-here"
      }
    }
  }
}
```

**Alternative: Direct SSE Connection**:
If using a custom MCP client that supports SSE:
```javascript
const eventSource = new EventSource('http://localhost:8081/sse');
eventSource.onmessage = function(event) {
  // Handle MCP messages
  const mcpMessage = JSON.parse(event.data);
};
```

**Transport Mode**:
- **HTTP JSON-RPC**: MCP protocol over HTTP at `/mcp` endpoint on port 8081

## MCP Tools

### 1. search_movies
Search for movies by title in the OMDB database.

**Parameters**:
- `title` (required): Movie title to search for
- `year` (optional): Year of release
- `type` (optional): Type of result (movie, series, or episode)

**Example**:
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "tools/call",
  "params": {
    "name": "search_movies",
    "arguments": {
      "title": "The Matrix",
      "year": "1999"
    }
  }
}
```

### 2. get_movie_details
Get detailed information about a specific movie by title.

**Parameters**:
- `title` (required): Movie title
- `year` (optional): Year of release
- `plot` (optional): Plot length ("short" or "full", default: "full")

**Example**:
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/call",
  "params": {
    "name": "get_movie_details",
    "arguments": {
      "title": "The Shawshank Redemption",
      "plot": "full"
    }
  }
}
```

### 3. get_movie_by_imdb_id
Get detailed information about a movie by IMDB ID.

**Parameters**:
- `imdbId` (required): IMDB ID (e.g., "tt0111161")
- `plot` (optional): Plot length ("short" or "full", default: "full")

**Example**:
```json
{
  "jsonrpc": "2.0",
  "id": "3",
  "method": "tools/call",
  "params": {
    "name": "get_movie_by_imdb_id",
    "arguments": {
      "imdbId": "tt0111161"
    }
  }
}
```

## MCP Protocol Implementation

This server implements the MCP 2024-11-05 specification using **Spring AI's native MCP Server support** with the following capabilities:

### Supported Methods
- **initialize**: Server initialization and capability negotiation (handled by Spring AI)
- **ping**: Connection testing and keep-alive (handled by Spring AI)
- **tools/list**: Dynamic tool discovery via Function bean registration
- **tools/call**: Tool execution through Spring AI Function interface
- **notifications/initialized**: Client initialization completion (handled by Spring AI)

### Spring AI Function Registration
Tools are automatically registered as Function beans and discovered by Spring AI:

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

### SSE Transport
Spring AI MCP Server uses Server-Sent Events for real-time communication:
- **Endpoint**: `GET /sse`
- **Content-Type**: `text/event-stream`
- **Connection**: Persistent bidirectional communication

### List Tools
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "tools/list"
}
```

## Configuration

The server can be configured using environment variables or `application.properties`:

### Core Configuration
```properties
# Server Configuration
server.port=8081

# OMDB API Configuration
omdb.api.url=https://www.omdbapi.com/
omdb.api.key=${OMDB_API_KEY:your-api-key-here}

# Spring AI MCP Server Configuration
spring.ai.mcp.server.enabled=true
spring.ai.mcp.server.name=OMDB Movie Database Server
spring.ai.mcp.server.version=0.2.0-SNAPSHOT
spring.ai.mcp.server.description=Spring AI MCP Server for searching and retrieving movie information from OMDB API
spring.ai.mcp.server.type=ASYNC
spring.ai.mcp.server.transport.type=SSE

# Cache Configuration
cache.expire-after-write=1h        # Cache TTL (Time To Live)
cache.maximum-size=1000           # Maximum number of cached entries
cache.record-stats=true           # Enable cache statistics

# Logging Configuration
logging.level.co.tyrell.omdb_mcp_server=INFO
logging.level.root=WARN
logging.level.org.springframework.cache=DEBUG  # For cache debugging
logging.level.org.springframework.ai.mcp=DEBUG  # For MCP debugging

# Actuator (Health Checks)
management.endpoints.web.exposure.include=health,info
management.endpoint.health.show-details=when-authorized
```

### Advanced Configuration
```properties
# WebClient Configuration
spring.webflux.timeout=30s
spring.reactor.netty.pool.max-connections=100

# JVM Tuning (for production)
JAVA_OPTS=-Xmx512m -Xms256m -XX:+UseG1GC
```

## 🧪 Testing & Validation

### Health Check
```bash
curl http://localhost:8081/actuator/health
```

### Cache Performance Testing
**Check cache statistics**:
```bash
curl http://localhost:8081/cache/stats
```

**Clear cache for testing**:
```bash
# Clear all caches
curl -X DELETE http://localhost:8081/cache/clear

# Clear specific cache
curl -X DELETE http://localhost:8081/cache/clear/movieSearch
```

**Test cache effectiveness**:
1. Make an initial request (cache miss):
   ```bash
   time curl -X POST http://localhost:8081/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"search_movies","arguments":{"title":"The Matrix"}}}'
   ```

2. Repeat the same request (cache hit - should be much faster):
   ```bash
   time curl -X POST http://localhost:8081/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"search_movies","arguments":{"title":"The Matrix"}}}'
   ```

3. Check cache statistics to see hit/miss ratios:
   ```bash
   curl http://localhost:8081/cache/stats
   ```

### MCP Protocol Testing

**Initialize the MCP connection**:
```bash
curl -X POST http://localhost:8081/mcp \
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
  }'
```

**List available tools**:
```bash
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/list"
  }'
```

**Search for movies**:
```bash
curl -X POST http://localhost:8081/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "search_movies",
      "arguments": {
        "title": "The Matrix",
        "year": "1999"
      }
    }
  }'
```

> 📋 **For comprehensive testing approaches and alternatives to MCP Inspector, see [MCP_TESTING_GUIDE.md](MCP_TESTING_GUIDE.md)**

### 🔍 Development & Debugging

**Run tests**:
```bash
./mvnw test
```

**Run cache-specific tests**:
```bash
./mvnw test -Dtest="*Cache*"
```

**Generate test coverage report**:
```bash
./mvnw jacoco:report
# View report at target/site/jacoco/index.html
```

**Build Docker image locally**:
```bash
docker build -t omdb-mcp-server:local .
```

## 🚀 CI/CD & Deployment

This project includes comprehensive GitHub Actions workflows:

- **🔄 Continuous Integration**: Automated testing, linting, and security scanning
- **📦 Build & Package**: JAR and Docker image creation
- **🐳 Docker**: Multi-platform container builds (AMD64/ARM64)
- **🏷️ Release**: Automated releases with GitHub Releases and container registry
- **🔒 Security**: Vulnerability scanning with Trivy
- **📈 Dependencies**: Automated dependency updates

### Deployment Options

1. **GitHub Container Registry**:
   ```bash
   docker pull ghcr.io/tyrell/omdb-mcp-server:latest
   ```

2. **Manual JAR Deployment**:
   - Download from [GitHub Releases](https://github.com/tyrell/omdb-mcp-server/releases)
   - Deploy on any Java 24+ environment

3. **Kubernetes**:
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: omdb-mcp-server
   spec:
     replicas: 2
     selector:
       matchLabels:
         app: omdb-mcp-server
     template:
       metadata:
         labels:
           app: omdb-mcp-server
       spec:
         containers:
         - name: omdb-mcp-server
           image: ghcr.io/tyrell/omdb-mcp-server:latest
           ports:
           - containerPort: 8081
           env:
           - name: OMDB_API_KEY
             valueFrom:
               secretKeyRef:
                 name: omdb-secret
                 key: api-key
   ```

## 📖 OpenAPI Documentation

The OMDB MCP Server provides comprehensive OpenAPI documentation for both the MCP protocol endpoints and administrative endpoints.

### Access Documentation

When the server is running, you can access the interactive API documentation at:

- **Swagger UI**: http://localhost:8081/swagger-ui/index.html
- **OpenAPI JSON**: http://localhost:8081/v3/api-docs

### API Endpoints

#### MCP Protocol Endpoints

**POST /mcp** - Handle MCP requests (JSON-RPC 2.0)
- **Purpose**: Main endpoint for Model Context Protocol communication
- **Content-Type**: application/json
- **Methods Supported**: 
  - `initialize` - Initialize MCP connection
  - `tools/list` - Get available tools
  - `tools/call` - Execute tool operations

**GET /mcp/health** - Health check endpoint
- **Purpose**: Verify the MCP server is running
- **Response**: Plain text status message

#### Cache Management Endpoints

**GET /cache/stats** - Get cache statistics
- **Purpose**: Retrieve detailed cache performance metrics
- **Response**: JSON with hit rates, miss rates, and entry counts

**DELETE /cache/clear** - Clear all caches
- **Purpose**: Remove all cached entries from all caches
- **Response**: JSON success message

**DELETE /cache/clear/{cacheName}** - Clear specific cache
- **Purpose**: Remove all entries from the specified cache
- **Parameters**: 
  - `cacheName` (path) - Name of the cache to clear
- **Response**: JSON success/error message

### OpenAPI Specification

<details>
<summary>Complete OpenAPI 3.0 Specification (Click to expand)</summary>

```yaml
openapi: 3.0.1
info:
  title: OMDB MCP Server API
  description: |
    A Model Context Protocol (MCP) Server that provides access to the Open Movie Database (OMDB) API.
    
    This server allows AI assistants and other MCP clients to search for movies and retrieve detailed movie information.
    
    ## Features
    - **Movie Search**: Search for movies by title, year, and type
    - **Movie Details**: Get detailed information about specific movies
    - **IMDB Integration**: Retrieve movies by IMDB ID
    - **Intelligent Caching**: Automatic caching of OMDB API responses
    - **MCP Compliance**: Full implementation of the Model Context Protocol 2024-11-05
    
    ## MCP Protocol
    The server implements the JSON-RPC 2.0 based Model Context Protocol for communication with AI assistants.
    Supported methods:
    - `initialize`: Initialize the MCP connection
    - `tools/list`: Get available tools
    - `tools/call`: Execute tool operations
    
    ## Available Tools
    - `search_movies`: Search for movies by title
    - `get_movie_details`: Get detailed movie information by title
    - `get_movie_by_imdb_id`: Get movie information by IMDB ID
  contact:
    name: OMDB MCP Server
    url: https://github.com/tyrell/omdb-mcp-server
  license:
    name: MIT License
    url: https://opensource.org/licenses/MIT
  version: 1.0.0
servers:
- url: http://localhost:8080
  description: Default server
paths:
  /mcp:
    post:
      tags:
      - MCP Controller
      summary: Handle MCP Request
      description: Processes Model Context Protocol requests including tool discovery and movie search operations
      operationId: handleMcpRequest
      requestBody:
        description: MCP JSON-RPC 2.0 request
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/McpRequest'
            examples:
              Initialize:
                summary: Initialize MCP connection
                value:
                  jsonrpc: "2.0"
                  id: "1"
                  method: initialize
                  params:
                    protocolVersion: "2024-11-05"
                    capabilities: {}
                    clientInfo:
                      name: example-client
                      version: 1.0.0
              List Tools:
                summary: Get available tools
                value:
                  jsonrpc: "2.0"
                  id: "2"
                  method: tools/list
                  params: {}
              Search Movies:
                summary: Search for movies
                value:
                  jsonrpc: "2.0"
                  id: "3"
                  method: tools/call
                  params:
                    name: search_movies
                    arguments:
                      title: The Matrix
                      year: "1999"
        required: true
      responses:
        "200":
          description: MCP response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/McpResponse'
              examples:
                Success Response:
                  summary: Successful MCP response
                  value:
                    jsonrpc: "2.0"
                    id: "3"
                    result:
                      content:
                      - type: text
                        text: |
                          🎬 The Matrix (1999)
                          
                          Rating: R
                          Runtime: 136 min
                          Genre: Action, Sci-Fi
                          Director: Lana Wachowski, Lilly Wachowski
                          Cast: Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss
                          IMDB Rating: 8.7/10
                          
                          Plot: When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence.
  /mcp/health:
    get:
      tags:
      - MCP Controller
      summary: Health Check
      description: Simple health check endpoint to verify the MCP server is running
      operationId: health
      responses:
        "200":
          description: Server is healthy
          content:
            text/plain:
              examples:
                default:
                  value: MCP Server is running
  /cache/stats:
    get:
      tags:
      - Cache Controller
      summary: Get Cache Statistics
      description: Returns detailed statistics for all active caches including hit rates, miss rates, and entry counts
      operationId: getCacheStats
      responses:
        "200":
          description: Cache statistics retrieved successfully
          content:
            application/json:
              examples:
                default:
                  value:
                    omdbMovies:
                      size: 42
                      hitCount: 156
                      missCount: 48
                      hitRate: 0.764706
                      missRate: 0.235294
                      requestCount: 204
                      loadCount: 48
                      evictionCount: 0
  /cache/clear:
    delete:
      tags:
      - Cache Controller
      summary: Clear All Caches
      description: Removes all entries from all active caches
      operationId: clearAllCaches
      responses:
        "200":
          description: All caches cleared successfully
          content:
            application/json:
              examples:
                default:
                  value:
                    message: All caches cleared successfully
  /cache/clear/{cacheName}:
    delete:
      tags:
      - Cache Controller
      summary: Clear Specific Cache
      description: Removes all entries from the specified cache
      operationId: clearCache
      parameters:
      - name: cacheName
        in: path
        description: Name of the cache to clear
        required: true
        schema:
          type: string
      responses:
        "200":
          description: Cache operation completed
          content:
            application/json:
              examples:
                Success:
                  summary: Cache cleared successfully
                  value:
                    message: Cache 'omdbMovies' cleared successfully
                Not Found:
                  summary: Cache not found
                  value:
                    error: Cache 'nonexistent' not found
components:
  schemas:
    McpRequest:
      type: object
      properties:
        jsonrpc:
          type: string
          description: JSON-RPC version
          example: "2.0"
          default: "2.0"
        id:
          type: string
          description: Request identifier
          example: "1"
        method:
          type: string
          description: Method name
          example: tools/call
          enum:
          - initialize
          - tools/list
          - tools/call
        params:
          type: object
          additionalProperties:
            type: object
          description: Method parameters
          example:
            name: search_movies
            arguments:
              title: The Matrix
      description: Model Context Protocol JSON-RPC 2.0 request
    McpResponse:
      type: object
      properties:
        jsonrpc:
          type: string
          description: JSON-RPC version
          example: "2.0"
          default: "2.0"
        id:
          type: string
          description: Request identifier
          example: "1"
        result:
          type: object
          description: Response result (present on success)
        error:
          $ref: '#/components/schemas/McpError'
      description: Model Context Protocol JSON-RPC 2.0 response
    McpError:
      type: object
      properties:
        code:
          type: integer
          format: int32
          description: Error code
          example: -32601
        message:
          type: string
          description: Error message
          example: Method not found
        data:
          type: object
          description: Additional error data
      description: MCP error details
```

</details>

### Example Usage

#### Initialize MCP Connection
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {
        "name": "example-client",
        "version": "1.0.0"
      }
    }
  }'
```

#### Get Available Tools
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/list",
    "params": {}
  }'
```

#### Search for Movies
```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "search_movies",
      "arguments": {
        "title": "The Matrix",
        "year": "1999",
        "type": "movie"
      }
    }
  }'
```

## API Response Format

All responses follow the MCP protocol format:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Formatted movie information..."
      }
    ]
  }
}
```

## Error Handling

The server returns standard JSON-RPC error responses:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": null
  }
}
```

Common error codes:
- `-32700`: Parse error
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup
1. **Fork the repository**
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/omdb-mcp-server
   cd omdb-mcp-server
   ```
3. **Set up development environment**:
   ```bash
   # Install Java 24 and Maven
   ./mvnw clean compile
   export OMDB_API_KEY=your-test-api-key
   ```
4. **Run tests**:
   ```bash
   ./mvnw test
   ```
5. **Make your changes and submit a PR**

### Code Style
- Follow Java conventions
- Write tests for new features
- Update documentation
- Ensure CI passes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Open Movie Database (OMDB)](http://www.omdbapi.com/) for providing the movie data API
- [Model Context Protocol](https://spec.modelcontextprotocol.io/) for the protocol specification
- [Spring Boot](https://spring.io/projects/spring-boot) for the excellent framework
- All contributors who help improve this project

## 📞 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/tyrell/omdb-mcp-server/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/tyrell/omdb-mcp-server/discussions)
- 📖 **Documentation**: [Project Wiki](https://github.com/tyrell/omdb-mcp-server/wiki)
- 🤖 **LLM Integration**: [LLM_INTEGRATION_GUIDE.md](LLM_INTEGRATION_GUIDE.md) - Detailed guide for AI assistant integration
- 🔒 **Security Issues**: See [SECURITY.md](SECURITY.md)
