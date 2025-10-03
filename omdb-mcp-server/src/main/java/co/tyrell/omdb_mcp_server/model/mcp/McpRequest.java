package co.tyrell.omdb_mcp_server.model.mcp;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.util.Map;

/**
 * Base MCP request structure
 */
@Data
@Schema(description = "Model Context Protocol JSON-RPC 2.0 request")
public class McpRequest {
    @Schema(description = "JSON-RPC version", example = "2.0", defaultValue = "2.0")
    private String jsonrpc = "2.0";
    
    @Schema(description = "Request identifier", example = "1")
    private String id;
    
    @Schema(description = "Method name", example = "tools/call", allowableValues = {"initialize", "tools/list", "tools/call"})
    private String method;
    
    @Schema(description = "Method parameters", example = "{\"name\": \"search_movies\", \"arguments\": {\"title\": \"The Matrix\"}}")
    private Map<String, Object> params;
}
