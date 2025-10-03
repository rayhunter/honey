package co.tyrell.omdb_mcp_server;

import co.tyrell.omdb_mcp_server.service.MovieSearchTools;
import co.tyrell.omdb_mcp_server.service.OmdbService;
import io.modelcontextprotocol.server.transport.WebFluxSseServerTransportProvider;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.TestPropertySource;
import org.springframework.web.reactive.function.server.RouterFunction;

import java.util.function.Function;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
@TestPropertySource(properties = {
    "omdb.api.key=test-key",
    "spring.ai.mcp.server.enabled=true",
    "spring.ai.mcp.server.name=Test OMDB MCP Server",
    "spring.ai.mcp.server.version=0.2.0-TEST",
    "spring.ai.mcp.server.type=ASYNC",
    "spring.ai.mcp.server.instructions=Test MCP server for OMDB movie database using Spring AI"
})
class OmdbMcpServerApplicationTests {

	@Autowired
	private MovieSearchTools movieSearchTools;
	
	@Autowired
	private OmdbService omdbService;
	
	@Autowired
	private WebFluxSseServerTransportProvider webFluxSseServerTransportProvider;
	
	@Autowired
	private RouterFunction<?> webfluxMcpRouterFunction;
	
	@Autowired
	private Function<MovieSearchTools.SearchMoviesRequest, String> searchMoviesFunction;
	
	@Autowired
	private Function<MovieSearchTools.MovieDetailsRequest, String> getMovieDetailsFunction;
	
	@Autowired
	private Function<MovieSearchTools.MovieByImdbIdRequest, String> getMovieByImdbIdFunction;

	@Test
	void contextLoads() {
		// Verify that all main components are loaded for Spring AI MCP Server
		assertThat(movieSearchTools).isNotNull();
		assertThat(omdbService).isNotNull();
		assertThat(webFluxSseServerTransportProvider).isNotNull();
		assertThat(webfluxMcpRouterFunction).isNotNull();
	}

	@Test
	void springAiMcpFunctionBeansArePresent() {
		// Verify that Spring AI MCP function beans are created
		assertThat(searchMoviesFunction).isNotNull();
		assertThat(getMovieDetailsFunction).isNotNull();
		assertThat(getMovieByImdbIdFunction).isNotNull();
	}
	
	@Test
	void movieSearchFunctionsWork() {
		// Verify MovieSearchTools function beans work correctly
		var searchRequest = new MovieSearchTools.SearchMoviesRequest("Inception", null, null);
		String searchResult = searchMoviesFunction.apply(searchRequest);
		assertThat(searchResult).isNotNull();
		
		var detailsRequest = new MovieSearchTools.MovieDetailsRequest("Inception", "2010", "short");
		String detailsResult = getMovieDetailsFunction.apply(detailsRequest);
		assertThat(detailsResult).isNotNull();
		
		var imdbRequest = new MovieSearchTools.MovieByImdbIdRequest("tt1375666", "short");
		String imdbResult = getMovieByImdbIdFunction.apply(imdbRequest);
		assertThat(imdbResult).isNotNull();
	}
	
	@Test
	void allRequiredBeansArePresent() {
		// Verify that Spring context contains all required beans for Spring AI MCP functionality
		assertThat(movieSearchTools).as("MovieSearchTools should be present").isNotNull();
		assertThat(omdbService).as("OmdbService should be present").isNotNull();
		assertThat(webFluxSseServerTransportProvider).as("WebFluxSseServerTransportProvider should be present").isNotNull();
		assertThat(webfluxMcpRouterFunction).as("WebFlux MCP RouterFunction should be present").isNotNull();
		assertThat(searchMoviesFunction).as("SearchMovies function should be present").isNotNull();
		assertThat(getMovieDetailsFunction).as("GetMovieDetails function should be present").isNotNull();
		assertThat(getMovieByImdbIdFunction).as("GetMovieByImdbId function should be present").isNotNull();
	}
}
