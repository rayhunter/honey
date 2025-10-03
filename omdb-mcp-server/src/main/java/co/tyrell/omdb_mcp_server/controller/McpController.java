package co.tyrell.omdb_mcp_server.controller;

import co.tyrell.omdb_mcp_server.model.mcp.McpRequest;
import co.tyrell.omdb_mcp_server.model.mcp.McpResponse;
import co.tyrell.omdb_mcp_server.service.McpService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;

/**
 * REST controller for handling MCP requests
 */
@RestController
@RequestMapping("/mcp")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "*")
@Tag(name = "MCP Controller", description = "Model Context Protocol endpoints for OMDB movie database access")
public class McpController {
    
    private final McpService mcpService;
    
    @PostMapping("")
    @Operation(
        summary = "Handle MCP Request",
        description = "Processes Model Context Protocol requests including tool discovery and movie search operations",
        requestBody = @io.swagger.v3.oas.annotations.parameters.RequestBody(
            description = "MCP JSON-RPC 2.0 request",
            required = true,
            content = @Content(
                mediaType = "application/json",
                schema = @Schema(implementation = McpRequest.class),
                examples = {
                    @ExampleObject(
                        name = "Initialize",
                        summary = "Initialize MCP connection",
                        value = """
                        {
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
                        }
                        """
                    ),
                    @ExampleObject(
                        name = "List Tools",
                        summary = "Get available tools",
                        value = """
                        {
                          "jsonrpc": "2.0",
                          "id": "2",
                          "method": "tools/list",
                          "params": {}
                        }
                        """
                    ),
                    @ExampleObject(
                        name = "Search Movies",
                        summary = "Search for movies",
                        value = """
                        {
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
                        }
                        """
                    )
                }
            )
        )
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "MCP response",
            content = @Content(
                mediaType = "application/json",
                schema = @Schema(implementation = McpResponse.class),
                examples = {
                    @ExampleObject(
                        name = "Success Response",
                        summary = "Successful MCP response",
                        value = """
                        {
                          "jsonrpc": "2.0",
                          "id": "3",
                          "result": {
                            "content": [{
                              "type": "text",
                              "text": "🎬 The Matrix (1999)\\n\\nRating: R\\nRuntime: 136 min\\nGenre: Action, Sci-Fi\\nDirector: Lana Wachowski, Lilly Wachowski\\nCast: Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss\\nIMDB Rating: 8.7/10\\n\\nPlot: When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence."
                            }]
                          }
                        }
                        """
                    )
                }
            )
        )
    })
    public Mono<ResponseEntity<McpResponse>> handleMcpRequest(
        @Parameter(description = "MCP JSON-RPC 2.0 request") @RequestBody McpRequest request) {
        log.info("Received MCP request: {} with ID: {}", request.getMethod(), request.getId());
        
        return mcpService.handleRequest(request)
                .map(response -> {
                    log.info("Sending MCP response for ID: {}", response.getId());
                    return ResponseEntity.ok(response);
                })
                .onErrorResume(error -> {
                    log.error("Error processing MCP request", error);
                    McpResponse errorResponse = new McpResponse();
                    errorResponse.setId(request.getId());
                    
                    McpResponse.McpError mcpError = new McpResponse.McpError();
                    mcpError.setCode(-32603);
                    mcpError.setMessage("Internal error: " + error.getMessage());
                    errorResponse.setError(mcpError);
                    
                    return Mono.just(ResponseEntity.ok(errorResponse));
                });
    }
    
    @GetMapping("/health")
    @Operation(
        summary = "Health Check",
        description = "Simple health check endpoint to verify the MCP server is running"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Server is healthy",
            content = @Content(
                mediaType = "text/plain",
                examples = @ExampleObject(value = "MCP Server is running")
            )
        )
    })
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("MCP Server is running");
    }
}
