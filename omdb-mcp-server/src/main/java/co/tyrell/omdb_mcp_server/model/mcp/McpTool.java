package co.tyrell.omdb_mcp_server.model.mcp;

import lombok.Data;

import java.util.List;
import java.util.Map;

/**
 * Enhanced MCP Tool definition with proper JSON Schema support
 */
@Data
public class McpTool {
    private String name;
    private String description;
    private InputSchema inputSchema;
    
    @Data
    public static class InputSchema {
        private String type = "object";
        private Map<String, Property> properties;
        private List<String> required;
        private Boolean additionalProperties = false;
        
        @Data
        public static class Property {
            private String type;
            private String description;
            private List<String> enumValues; // for enum constraints
            private String pattern; // for regex patterns
            private Integer minLength;
            private Integer maxLength;
            private Object defaultValue;
            private List<String> examples;
        }
    }
}
