package co.tyrell.omdb_mcp_server.model.mcp;

import lombok.Data;

/**
 * MCP Resource definition
 */
@Data
public class McpResource {
    private String uri;
    private String name;
    private String description;
    private String mimeType;
}
