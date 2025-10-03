package co.tyrell.omdb_mcp_server.service;

import co.tyrell.omdb_mcp_server.model.omdb.OmdbMovie;
import co.tyrell.omdb_mcp_server.model.omdb.OmdbSearchResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.quality.Strictness;
import org.mockito.junit.jupiter.MockitoSettings;
import reactor.core.publisher.Mono;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
@MockitoSettings(strictness = Strictness.LENIENT)
class MovieSearchToolsTest {

    @Mock
    private OmdbService omdbService;

    private MovieSearchTools movieSearchTools;

    @BeforeEach
    void setUp() {
        movieSearchTools = new MovieSearchTools(omdbService);
    }

    @Test
    void searchMovies_WithTitle_ShouldReturnFormattedResults() {
        // Given
        OmdbSearchResponse searchResponse = new OmdbSearchResponse();
        OmdbSearchResponse.SearchResult[] searchResults = new OmdbSearchResponse.SearchResult[1];
        OmdbSearchResponse.SearchResult result = new OmdbSearchResponse.SearchResult();
        result.setTitle("Inception");
        result.setYear("2010");
        result.setImdbId("tt1375666");
        result.setType("movie");
        result.setPoster("https://example.com/poster.jpg");
        searchResults[0] = result;
        
        searchResponse.setSearch(searchResults);
        searchResponse.setTotalResults("1");
        searchResponse.setResponse("True");
        
        when(omdbService.searchMovies(eq("Inception"), eq(null), eq(null)))
            .thenReturn(Mono.just(searchResponse));

        // When
        String resultString = movieSearchTools.searchMovies("Inception", null, null);

        // Then
        assertThat(resultString).isNotNull();
        assertThat(resultString).contains("Inception");
        assertThat(resultString).contains("2010");
        assertThat(resultString).contains("tt1375666");
    }

    @Test
    void searchMovies_WithTitleAndYear_ShouldReturnFormattedResults() {
        // Given
        OmdbSearchResponse searchResponse = new OmdbSearchResponse();
        OmdbSearchResponse.SearchResult[] searchResults = new OmdbSearchResponse.SearchResult[1];
        OmdbSearchResponse.SearchResult result = new OmdbSearchResponse.SearchResult();
        result.setTitle("Inception");
        result.setYear("2010");
        result.setImdbId("tt1375666");
        searchResults[0] = result;
        
        searchResponse.setSearch(searchResults);
        searchResponse.setTotalResults("1");
        searchResponse.setResponse("True");
        
        when(omdbService.searchMovies(eq("Inception"), eq("2010"), eq(null)))
            .thenReturn(Mono.just(searchResponse));

        // When
        String resultString = movieSearchTools.searchMovies("Inception", "2010", null);

        // Then
        assertThat(resultString).isNotNull();
        assertThat(resultString).contains("Inception");
        assertThat(resultString).contains("2010");
    }

    @Test
    void searchMovies_WithError_ShouldReturnErrorMessage() {
        // Given
        when(omdbService.searchMovies(anyString(), anyString(), anyString()))
            .thenReturn(Mono.error(new RuntimeException("Movie not found!")));

        // When
        String result = movieSearchTools.searchMovies("NonexistentMovie", null, null);

        // Then
        assertThat(result).isNotNull();
        assertThat(result).contains("Error");
        assertThat(result).contains("Cannot invoke");
    }

    @Test
    void getMovieDetails_WithTitleAndYear_ShouldReturnFormattedDetails() {
        // Given
        OmdbMovie movie = createTestMovie();
        when(omdbService.getMovieByTitle(eq("Inception"), eq("2010"), eq("short")))
            .thenReturn(Mono.just(movie));

        // When
        String result = movieSearchTools.getMovieDetails("Inception", "2010", "short");

        // Then
        assertThat(result).isNotNull();
        assertThat(result).contains("Inception");
        assertThat(result).contains("2010");
        assertThat(result).contains("Christopher Nolan");
    }

    @Test
    void getMovieByImdbId_WithValidId_ShouldReturnFormattedDetails() {
        // Given
        OmdbMovie movie = createTestMovie();
        when(omdbService.getMovieByImdbId(eq("tt1375666"), eq("short")))
            .thenReturn(Mono.just(movie));

        // When
        String result = movieSearchTools.getMovieByImdbId("tt1375666", "short");

        // Then
        assertThat(result).isNotNull();
        assertThat(result).contains("Inception");
        assertThat(result).contains("tt1375666");
        assertThat(result).contains("Christopher Nolan");
    }

    @Test
    void getMovieDetails_WithError_ShouldReturnErrorMessage() {
        // Given
        when(omdbService.getMovieByTitle(anyString(), anyString(), anyString()))
            .thenReturn(Mono.error(new RuntimeException("Service error")));

        // When
        String result = movieSearchTools.getMovieDetails("Unknown", "2024", "short");

        // Then
        assertThat(result).isNotNull();
        assertThat(result).contains("Error");
        assertThat(result).contains("Service error");
    }

    @Test
    void getMovieByImdbId_WithError_ShouldReturnErrorMessage() {
        // Given
        when(omdbService.getMovieByImdbId(anyString(), anyString()))
            .thenReturn(Mono.error(new RuntimeException("Invalid ID")));

        // When
        String result = movieSearchTools.getMovieByImdbId("invalidId", "short");

        // Then
        assertThat(result).isNotNull();
        assertThat(result).contains("Error");
        assertThat(result).contains("Invalid ID");
    }

    private OmdbMovie createTestMovie() {
        OmdbMovie movie = new OmdbMovie();
        movie.setTitle("Inception");
        movie.setYear("2010");
        movie.setImdbId("tt1375666");
        movie.setType("movie");
        movie.setPoster("https://example.com/poster.jpg");
        movie.setDirector("Christopher Nolan");
        movie.setWriter("Christopher Nolan");
        movie.setActors("Leonardo DiCaprio, Marion Cotillard");
        movie.setPlot("A thief who steals corporate secrets through dream-sharing technology...");
        movie.setRated("PG-13");
        movie.setRuntime("148 min");
        movie.setGenre("Action, Sci-Fi, Thriller");
        movie.setImdbRating("8.8");
        movie.setResponse("True");
        return movie;
    }
}
