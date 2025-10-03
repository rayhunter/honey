package co.tyrell.omdb_mcp_server.model.omdb;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

/**
 * OMDB API Search response model
 */
@Data
public class OmdbSearchResponse {
    @JsonProperty("Search")
    private SearchResult[] search;
    
    @JsonProperty("totalResults")
    private String totalResults;
    
    @JsonProperty("Response")
    private String response;
    
    @JsonProperty("Error")
    private String error;
    
    @Data
    public static class SearchResult {
        @JsonProperty("Title")
        private String title;
        
        @JsonProperty("Year")
        private String year;
        
        @JsonProperty("imdbID")
        private String imdbId;
        
        @JsonProperty("Type")
        private String type;
        
        @JsonProperty("Poster")
        private String poster;
    }
}
