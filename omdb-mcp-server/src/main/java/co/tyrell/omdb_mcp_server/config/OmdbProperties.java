package co.tyrell.omdb_mcp_server.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * Configuration properties for OMDB API
 */
@Configuration
@ConfigurationProperties(prefix = "omdb.api")
@Data
public class OmdbProperties {
    private String url = "http://www.omdbapi.com/";
    private String key;
}
