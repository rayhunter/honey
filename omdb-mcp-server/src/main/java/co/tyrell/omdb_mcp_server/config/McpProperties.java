package co.tyrell.omdb_mcp_server.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration properties for MCP Server
 */
@Configuration
@ConfigurationProperties(prefix = "mcp.server")
@Data
public class McpProperties {
    private String name = "OMDB Movie Database Server";
    private String version = "1.0.0";
    private String description = "MCP Server for searching and retrieving movie information from OMDB API";
}
