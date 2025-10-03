package co.tyrell.omdb_mcp_server.model.mcp;

import com.fasterxml.jackson.annotation.JsonInclude;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

/**
 * Base MCP response structure
 */
@Data
@JsonInclude(JsonInclude.Include.NON_NULL)
@Schema(description = "Model Context Protocol JSON-RPC 2.0 response")
public class McpResponse {
    @Schema(description = "JSON-RPC version", example = "2.0", defaultValue = "2.0")
    private String jsonrpc = "2.0";
    
    @Schema(description = "Request identifier", example = "1")
    private String id;
    
    @Schema(description = "Response result (present on success)")
    private Object result;
    
    @Schema(description = "Error information (present on failure)")
    private McpError error;
    
    @Data
    @Schema(description = "MCP error details")
    public static class McpError {
        @Schema(description = "Error code", example = "-32601")
        private int code;
        
        @Schema(description = "Error message", example = "Method not found")
        private String message;
        
        @Schema(description = "Additional error data")
        private Object data;
    }
}
