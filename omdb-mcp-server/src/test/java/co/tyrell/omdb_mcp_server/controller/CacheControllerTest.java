package co.tyrell.omdb_mcp_server.controller;

import co.tyrell.omdb_mcp_server.config.CacheConfig;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.reactive.WebFluxTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.cache.CacheManager;
import org.springframework.cache.caffeine.CaffeineCache;
import org.springframework.test.web.reactive.server.WebTestClient;

import java.util.Set;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

@WebFluxTest(CacheController.class)
class CacheControllerTest {

    @Autowired
    private WebTestClient webTestClient;

    @MockBean
    private CacheManager cacheManager;

    @Test
    void testGetCacheStats() throws Exception {
        // Create a real Caffeine cache with stats enabled for testing
        Cache<Object, Object> nativeCache = Caffeine.newBuilder()
                .recordStats()
                .build();
        
        // Create a mock CaffeineCache that returns our real native cache
        CaffeineCache mockCaffeineCache = mock(CaffeineCache.class);
        when(mockCaffeineCache.getNativeCache()).thenReturn(nativeCache);
        
        when(cacheManager.getCacheNames()).thenReturn(Set.of(CacheConfig.MOVIE_SEARCH_CACHE));
        when(cacheManager.getCache(CacheConfig.MOVIE_SEARCH_CACHE)).thenReturn(mockCaffeineCache);

        webTestClient.get()
                .uri("/cache/stats")
                .exchange()
                .expectStatus().isOk()
                .expectHeader().contentType("application/json");
    }

    @Test
    void testClearAllCaches() throws Exception {
        // Create a mock CaffeineCache
        CaffeineCache mockCaffeineCache = mock(CaffeineCache.class);
        
        when(cacheManager.getCacheNames()).thenReturn(Set.of(CacheConfig.MOVIE_SEARCH_CACHE));
        when(cacheManager.getCache(CacheConfig.MOVIE_SEARCH_CACHE)).thenReturn(mockCaffeineCache);

        webTestClient.delete()
                .uri("/cache/clear")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.message").isEqualTo("All caches cleared successfully");
    }

    @Test
    void testClearSpecificCache() throws Exception {
        // Create a mock CaffeineCache
        CaffeineCache mockCaffeineCache = mock(CaffeineCache.class);
        
        when(cacheManager.getCache(CacheConfig.MOVIE_SEARCH_CACHE)).thenReturn(mockCaffeineCache);

        webTestClient.delete()
                .uri("/cache/clear/" + CacheConfig.MOVIE_SEARCH_CACHE)
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.message").isEqualTo("Cache '" + CacheConfig.MOVIE_SEARCH_CACHE + "' cleared successfully");
    }

    @Test
    void testClearNonExistentCache() throws Exception {
        when(cacheManager.getCache("nonexistent")).thenReturn(null);

        webTestClient.delete()
                .uri("/cache/clear/nonexistent")
                .exchange()
                .expectStatus().isOk()
                .expectBody()
                .jsonPath("$.error").isEqualTo("Cache 'nonexistent' not found");
    }
}
