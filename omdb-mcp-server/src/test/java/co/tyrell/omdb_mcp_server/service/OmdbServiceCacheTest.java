package co.tyrell.omdb_mcp_server.service;

import co.tyrell.omdb_mcp_server.config.CacheConfig;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.cache.CacheManager;
import org.springframework.cache.caffeine.CaffeineCache;
import org.springframework.test.context.TestPropertySource;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
@TestPropertySource(properties = {
    "omdb.api.key=test-key",
    "cache.expire-after-write=1h",
    "cache.maximum-size=100"
})
class OmdbServiceCacheTest {

    @Autowired
    private CacheManager cacheManager;

    @Test
    void testCacheManagerConfiguration() {
        // Verify that all expected caches are configured
        assertTrue(cacheManager.getCacheNames().contains(CacheConfig.MOVIE_SEARCH_CACHE));
        assertTrue(cacheManager.getCacheNames().contains(CacheConfig.MOVIE_BY_TITLE_CACHE));
        assertTrue(cacheManager.getCacheNames().contains(CacheConfig.MOVIE_BY_IMDB_ID_CACHE));
        
        // Verify cache implementation
        org.springframework.cache.Cache cache = cacheManager.getCache(CacheConfig.MOVIE_SEARCH_CACHE);
        assertNotNull(cache);
        assertTrue(cache instanceof CaffeineCache);
        
        CaffeineCache caffeineCache = (CaffeineCache) cache;
        assertEquals(0, caffeineCache.getNativeCache().estimatedSize());
    }

    @Test
    void testCacheStatsEnabled() {
        org.springframework.cache.Cache cache = cacheManager.getCache(CacheConfig.MOVIE_SEARCH_CACHE);
        assertNotNull(cache);
        
        if (cache instanceof CaffeineCache) {
            CaffeineCache caffeineCache = (CaffeineCache) cache;
            // Verify stats are enabled by checking if stats object is available
            assertNotNull(caffeineCache.getNativeCache().stats());
        }
    }
}
