package co.tyrell.omdb_mcp_server.service;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * Movie search tools for Spring AI MCP integration
 * Using method-based tool definitions
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class MovieSearchTools {
    
    private final OmdbService omdbService;
    
    /**
     * Search for movies by title in the OMDB database
     */
    public String searchMovies(String title, String year, String type) {
        log.info("Searching movies with title: {}, year: {}, type: {}", title, year, type);
        
        try {
            var searchResponse = omdbService.searchMovies(title, year, type).block();
            
            if (searchResponse != null && "True".equals(searchResponse.getResponse())) {
                return formatSearchResults(searchResponse);
            } else {
                return "No movies found: " + (searchResponse != null ? searchResponse.getError() : "Unknown error");
            }
        } catch (Exception e) {
            log.error("Error searching movies", e);
            return "Error searching movies: " + e.getMessage();
        }
    }
    
    /**
     * Get detailed information about a specific movie by title
     */
    public String getMovieDetails(String title, String year, String plot) {
        log.info("Getting movie details for title: {}, year: {}, plot: {}", title, year, plot);
        
        try {
            var movie = omdbService.getMovieByTitle(title, year, plot).block();
            
            if (movie != null && "True".equals(movie.getResponse())) {
                return formatMovieDetails(movie);
            } else {
                return "Movie not found: " + (movie != null ? movie.getError() : "Unknown error");
            }
        } catch (Exception e) {
            log.error("Error getting movie details", e);
            return "Error getting movie details: " + e.getMessage();
        }
    }
    
    /**
     * Get detailed information about a movie by IMDB ID
     */
    public String getMovieByImdbId(String imdbId, String plot) {
        log.info("Getting movie by IMDB ID: {}, plot: {}", imdbId, plot);
        
        try {
            var movie = omdbService.getMovieByImdbId(imdbId, plot).block();
            
            if (movie != null && "True".equals(movie.getResponse())) {
                return formatMovieDetails(movie);
            } else {
                return "Movie not found: " + (movie != null ? movie.getError() : "Unknown error");
            }
        } catch (Exception e) {
            log.error("Error getting movie by IMDB ID", e);
            return "Error getting movie by IMDB ID: " + e.getMessage();
        }
    }
    
    private String formatSearchResults(co.tyrell.omdb_mcp_server.model.omdb.OmdbSearchResponse searchResponse) {
        StringBuilder sb = new StringBuilder();
        sb.append("Search Results (").append(searchResponse.getTotalResults()).append(" total):\n\n");
        
        if (searchResponse.getSearch() != null) {
            for (int i = 0; i < searchResponse.getSearch().length; i++) {
                var movie = searchResponse.getSearch()[i];
                sb.append(i + 1).append(". ");
                sb.append(movie.getTitle()).append(" (").append(movie.getYear()).append(")\n");
                sb.append("   Type: ").append(movie.getType()).append("\n");
                sb.append("   IMDB ID: ").append(movie.getImdbId()).append("\n\n");
            }
        }
        
        return sb.toString();
    }
    
    private String formatMovieDetails(co.tyrell.omdb_mcp_server.model.omdb.OmdbMovie movie) {
        StringBuilder sb = new StringBuilder();
        sb.append("🎬 ").append(movie.getTitle()).append(" (").append(movie.getYear()).append(")\n");
        
        if (movie.getImdbId() != null) sb.append("IMDB ID: ").append(movie.getImdbId()).append("\n");
        if (movie.getRated() != null) sb.append("Rating: ").append(movie.getRated()).append("\n");
        if (movie.getRuntime() != null) sb.append("Runtime: ").append(movie.getRuntime()).append("\n");
        if (movie.getGenre() != null) sb.append("Genre: ").append(movie.getGenre()).append("\n");
        if (movie.getDirector() != null) sb.append("Director: ").append(movie.getDirector()).append("\n");
        if (movie.getActors() != null) sb.append("Cast: ").append(movie.getActors()).append("\n");
        if (movie.getImdbRating() != null) sb.append("IMDB Rating: ").append(movie.getImdbRating()).append("/10\n");
        if (movie.getMetascore() != null) sb.append("Metacritic Score: ").append(movie.getMetascore()).append("/100\n");
        
        sb.append("\nPlot:\n").append(movie.getPlot() != null ? movie.getPlot() : "No plot available");
        
        if (movie.getAwards() != null) {
            sb.append("\n\nAwards: ").append(movie.getAwards());
        }
        
        return sb.toString();
    }
    
    // Request record classes for type safety with JSON Schema annotations
    @Schema(description = "Request to search for movies by title")
    public record SearchMoviesRequest(
        @Schema(description = "Movie title to search for", required = true)
        String title,
        @Schema(description = "Release year (optional)")
        String year,
        @Schema(description = "Type: movie, series, or episode (optional)")
        String type
    ) {}
    
    @Schema(description = "Request to get detailed movie information")
    public record MovieDetailsRequest(
        @Schema(description = "Movie title", required = true)
        String title,
        @Schema(description = "Release year (optional)")
        String year,
        @Schema(description = "Plot length: short or full (default: full)")
        String plot
    ) {}
    
    @Schema(description = "Request to get movie by IMDB ID")
    public record MovieByImdbIdRequest(
        @Schema(description = "IMDB ID (e.g., tt0133093)", required = true)
        String imdbId,
        @Schema(description = "Plot length: short or full (default: full)")
        String plot
    ) {}
}
