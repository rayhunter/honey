package co.tyrell.omdb_mcp_server.controller;

import com.github.benmanes.caffeine.cache.Cache;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.CacheManager;
import org.springframework.cache.caffeine.CaffeineCache;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * Controller for cache management and statistics
 */
@RestController
@RequestMapping("/cache")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Cache Controller", description = "Cache management and statistics endpoints")
public class CacheController {
    
    private final CacheManager cacheManager;
    
    /**
     * Get cache statistics for all caches
     */
    @GetMapping("/stats")
    @Operation(
        summary = "Get Cache Statistics",
        description = "Returns detailed statistics for all active caches including hit rates, miss rates, and entry counts"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Cache statistics retrieved successfully",
            content = @Content(
                mediaType = "application/json",
                examples = @ExampleObject(
                    value = """
                    {
                      "omdbMovies": {
                        "size": 42,
                        "hitCount": 156,
                        "missCount": 48,
                        "hitRate": 0.764706,
                        "missRate": 0.235294,
                        "requestCount": 204,
                        "loadCount": 48,
                        "evictionCount": 0
                      }
                    }
                    """
                )
            )
        )
    })
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        
        for (String cacheName : cacheManager.getCacheNames()) {
            org.springframework.cache.Cache cache = cacheManager.getCache(cacheName);
            if (cache instanceof CaffeineCache) {
                CaffeineCache caffeineCache = (CaffeineCache) cache;
                Cache<Object, Object> nativeCache = caffeineCache.getNativeCache();
                
                Map<String, Object> cacheStats = new HashMap<>();
                cacheStats.put("size", nativeCache.estimatedSize());
                cacheStats.put("hitCount", nativeCache.stats().hitCount());
                cacheStats.put("missCount", nativeCache.stats().missCount());
                cacheStats.put("hitRate", nativeCache.stats().hitRate());
                cacheStats.put("missRate", nativeCache.stats().missRate());
                cacheStats.put("requestCount", nativeCache.stats().requestCount());
                cacheStats.put("loadCount", nativeCache.stats().loadCount());
                cacheStats.put("evictionCount", nativeCache.stats().evictionCount());
                
                stats.put(cacheName, cacheStats);
            }
        }
        
        return stats;
    }
    
    /**
     * Clear all caches
     */
    @DeleteMapping("/clear")
    @Operation(
        summary = "Clear All Caches",
        description = "Removes all entries from all active caches"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "All caches cleared successfully",
            content = @Content(
                mediaType = "application/json",
                examples = @ExampleObject(
                    value = """
                    {
                      "message": "All caches cleared successfully"
                    }
                    """
                )
            )
        )
    })
    public Map<String, String> clearAllCaches() {
        for (String cacheName : cacheManager.getCacheNames()) {
            org.springframework.cache.Cache cache = cacheManager.getCache(cacheName);
            if (cache != null) {
                cache.clear();
                log.info("Cleared cache: {}", cacheName);
            }
        }
        return Map.of("message", "All caches cleared successfully");
    }
    
    /**
     * Clear specific cache
     */
    @DeleteMapping("/clear/{cacheName}")
    @Operation(
        summary = "Clear Specific Cache",
        description = "Removes all entries from the specified cache"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Cache operation completed",
            content = @Content(
                mediaType = "application/json",
                examples = {
                    @ExampleObject(
                        name = "Success",
                        summary = "Cache cleared successfully",
                        value = """
                        {
                          "message": "Cache 'omdbMovies' cleared successfully"
                        }
                        """
                    ),
                    @ExampleObject(
                        name = "Not Found",
                        summary = "Cache not found",
                        value = """
                        {
                          "error": "Cache 'nonexistent' not found"
                        }
                        """
                    )
                }
            )
        )
    })
    public Map<String, String> clearCache(
        @Parameter(description = "Name of the cache to clear") @PathVariable String cacheName) {
        org.springframework.cache.Cache cache = cacheManager.getCache(cacheName);
        if (cache != null) {
            cache.clear();
            log.info("Cleared cache: {}", cacheName);
            return Map.of("message", "Cache '" + cacheName + "' cleared successfully");
        } else {
            return Map.of("error", "Cache '" + cacheName + "' not found");
        }
    }
}
