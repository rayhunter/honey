package co.tyrell.omdb_mcp_server.config;

import com.github.benmanes.caffeine.cache.Caffeine;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.caffeine.CaffeineCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import lombok.Data;

import java.time.Duration;

/**
 * Cache configuration for OMDB API responses
 */
@Configuration
@EnableCaching
@ConfigurationProperties(prefix = "cache")
@Data
public class CacheConfig {
    
    // Cache configuration properties
    private Duration expireAfterWrite = Duration.ofHours(1);
    private long maximumSize = 1000;
    private boolean recordStats = true;
    
    public static final String MOVIE_SEARCH_CACHE = "movieSearch";
    public static final String MOVIE_BY_TITLE_CACHE = "movieByTitle";
    public static final String MOVIE_BY_IMDB_ID_CACHE = "movieByImdbId";
    
    @Bean
    public CacheManager cacheManager() {
        CaffeineCacheManager cacheManager = new CaffeineCacheManager();
        cacheManager.setCaffeine(caffeineCacheBuilder());
        cacheManager.setAsyncCacheMode(true); // Enable async cache mode for reactive types
        cacheManager.setCacheNames(java.util.List.of(
            MOVIE_SEARCH_CACHE,
            MOVIE_BY_TITLE_CACHE,
            MOVIE_BY_IMDB_ID_CACHE
        ));
        return cacheManager;
    }
    
    @Bean
    public Caffeine<Object, Object> caffeineCacheBuilder() {
        return Caffeine.newBuilder()
                .expireAfterWrite(expireAfterWrite)
                .maximumSize(maximumSize)
                .recordStats();
    }
}
