package co.tyrell.omdb_mcp_server.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

/**
 * OpenAPI configuration for the OMDB MCP Server
 */
@Configuration
public class OpenApiConfig {

    @Value("${server.port:8081}")
    private String serverPort;

    @Bean
    public OpenAPI customOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("OMDB MCP Server API")
                        .version("1.0.0")
                        .description("""
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
                                """)
                        .contact(new Contact()
                                .name("OMDB MCP Server")
                                .url("https://github.com/tyrell/omdb-mcp-server"))
                        .license(new License()
                                .name("MIT License")
                                .url("https://opensource.org/licenses/MIT")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:" + serverPort)
                                .description("Local development server"),
                        new Server()
                                .url("http://localhost:8080")
                                .description("Default server")));
    }
}
