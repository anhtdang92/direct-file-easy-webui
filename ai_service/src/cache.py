from typing import Any, Dict, Optional, List, Tuple, Set
import time
import hashlib
import json
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.base import BaseHTTPMiddleware
import gzip
from collections import OrderedDict
import asyncio
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheConfig:
    """Configuration for endpoint-specific caching rules."""
    def __init__(
        self,
        ttl: int = 60,
        vary_by: List[str] = None,
        max_size: int = 1000,
        compress: bool = True,
        skip_cache: bool = False,
        stale_while_revalidate: int = 0,
        must_revalidate: bool = False,
        private: bool = False,
        no_store: bool = False
    ):
        self.ttl = ttl
        self.vary_by = vary_by or []
        self.max_size = max_size
        self.compress = compress
        self.skip_cache = skip_cache
        self.stale_while_revalidate = stale_while_revalidate
        self.must_revalidate = must_revalidate
        self.private = private
        self.no_store = no_store

# Define cache configurations for different endpoints
CACHE_CONFIGS = {
    # Health check endpoint - very short TTL, public
    "/health": CacheConfig(
        ttl=30,
        vary_by=["Accept-Encoding"],
        max_size=10,
        compress=True,
        stale_while_revalidate=5
    ),

    # Document processing endpoints
    "/process": CacheConfig(
        ttl=3600,  # 1 hour
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=100,
        compress=True,
        must_revalidate=True
    ),
    "/process/w2": CacheConfig(
        ttl=7200,  # 2 hours for W-2 forms
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=50,
        compress=True,
        must_revalidate=True
    ),
    "/process/1099": CacheConfig(
        ttl=7200,  # 2 hours for 1099 forms
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=50,
        compress=True,
        must_revalidate=True
    ),
    "/process/batch": CacheConfig(
        ttl=1800,  # 30 minutes for batch processing
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=20,
        compress=True,
        must_revalidate=True
    ),
    "/process/status": CacheConfig(
        ttl=60,  # 1 minute for processing status
        vary_by=["Authorization"],
        max_size=100,
        compress=True,
        stale_while_revalidate=30
    ),

    # Analysis endpoints
    "/analyze": CacheConfig(
        ttl=1800,  # 30 minutes
        vary_by=["Authorization", "Accept-Encoding", "Content-Type"],
        max_size=200,
        compress=True,
        stale_while_revalidate=300  # 5 minutes stale-while-revalidate
    ),
    "/analyze/w2": CacheConfig(
        ttl=3600,  # 1 hour for W-2 analysis
        vary_by=["Authorization", "Accept-Encoding", "Content-Type"],
        max_size=100,
        compress=True,
        stale_while_revalidate=600  # 10 minutes stale-while-revalidate
    ),
    "/analyze/1099": CacheConfig(
        ttl=3600,  # 1 hour for 1099 analysis
        vary_by=["Authorization", "Accept-Encoding", "Content-Type"],
        max_size=100,
        compress=True,
        stale_while_revalidate=600  # 10 minutes stale-while-revalidate
    ),
    "/analyze/compare": CacheConfig(
        ttl=900,  # 15 minutes for comparison analysis
        vary_by=["Authorization", "Accept-Encoding", "Content-Type"],
        max_size=50,
        compress=True,
        must_revalidate=True
    ),
    "/analyze/summary": CacheConfig(
        ttl=1800,  # 30 minutes for analysis summaries
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=200,
        compress=True,
        stale_while_revalidate=300
    ),

    # User-specific endpoints
    "/user/profile": CacheConfig(
        ttl=300,  # 5 minutes
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=1000,
        compress=True,
        private=True,
        must_revalidate=True
    ),
    "/user/documents": CacheConfig(
        ttl=600,  # 10 minutes
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=500,
        compress=True,
        private=True,
        must_revalidate=True
    ),
    "/user/settings": CacheConfig(
        ttl=1800,  # 30 minutes
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=100,
        compress=True,
        private=True,
        must_revalidate=True
    ),
    "/user/preferences": CacheConfig(
        ttl=3600,  # 1 hour
        vary_by=["Authorization"],
        max_size=100,
        compress=True,
        private=True
    ),
    "/user/notifications": CacheConfig(
        ttl=60,  # 1 minute
        vary_by=["Authorization"],
        max_size=100,
        compress=True,
        private=True,
        stale_while_revalidate=30
    ),
    "/user/activity": CacheConfig(
        ttl=300,  # 5 minutes
        vary_by=["Authorization"],
        max_size=200,
        compress=True,
        private=True,
        stale_while_revalidate=60
    ),

    # Public endpoints
    "/public/tax-rates": CacheConfig(
        ttl=86400,  # 24 hours
        vary_by=["Accept-Encoding"],
        max_size=10,
        compress=True,
        stale_while_revalidate=3600  # 1 hour stale-while-revalidate
    ),
    "/public/deductions": CacheConfig(
        ttl=86400,  # 24 hours
        vary_by=["Accept-Encoding"],
        max_size=20,
        compress=True,
        stale_while_revalidate=3600  # 1 hour stale-while-revalidate
    ),
    "/public/faq": CacheConfig(
        ttl=43200,  # 12 hours
        vary_by=["Accept-Encoding"],
        max_size=10,
        compress=True,
        stale_while_revalidate=1800  # 30 minutes stale-while-revalidate
    ),
    "/public/updates": CacheConfig(
        ttl=3600,  # 1 hour
        vary_by=["Accept-Encoding"],
        max_size=20,
        compress=True,
        stale_while_revalidate=300  # 5 minutes stale-while-revalidate
    ),
    "/public/announcements": CacheConfig(
        ttl=1800,  # 30 minutes
        vary_by=["Accept-Encoding"],
        max_size=10,
        compress=True,
        stale_while_revalidate=300  # 5 minutes stale-while-revalidate
    ),

    # Search and list endpoints
    "/search": CacheConfig(
        ttl=300,  # 5 minutes
        vary_by=["Authorization", "Accept-Encoding", "Content-Type"],
        max_size=1000,
        compress=True,
        stale_while_revalidate=60  # 1 minute stale-while-revalidate
    ),
    "/list/documents": CacheConfig(
        ttl=300,  # 5 minutes
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=500,
        compress=True,
        stale_while_revalidate=60  # 1 minute stale-while-revalidate
    ),
    "/list/templates": CacheConfig(
        ttl=3600,  # 1 hour
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=100,
        compress=True,
        stale_while_revalidate=300  # 5 minutes stale-while-revalidate
    ),
    "/list/categories": CacheConfig(
        ttl=7200,  # 2 hours
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=50,
        compress=True,
        stale_while_revalidate=600  # 10 minutes stale-while-revalidate
    ),

    # Export and download endpoints
    "/export/pdf": CacheConfig(
        ttl=300,  # 5 minutes
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=50,
        compress=True,
        must_revalidate=True
    ),
    "/export/csv": CacheConfig(
        ttl=300,  # 5 minutes
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=50,
        compress=True,
        must_revalidate=True
    ),
    "/download/template": CacheConfig(
        ttl=3600,  # 1 hour
        vary_by=["Authorization", "Accept-Encoding"],
        max_size=100,
        compress=True,
        stale_while_revalidate=300  # 5 minutes stale-while-revalidate
    ),

    # Cache management endpoints - no caching
    "/cache/stats": CacheConfig(skip_cache=True),
    "/cache/invalidate": CacheConfig(skip_cache=True),
    "/cache/clear": CacheConfig(skip_cache=True),
    "/cache/warm": CacheConfig(skip_cache=True),

    # Authentication endpoints - no caching
    "/auth/login": CacheConfig(skip_cache=True),
    "/auth/register": CacheConfig(skip_cache=True),
    "/auth/refresh": CacheConfig(skip_cache=True),
    "/auth/logout": CacheConfig(skip_cache=True),
    "/auth/verify": CacheConfig(skip_cache=True),
    "/auth/reset-password": CacheConfig(skip_cache=True),
    "/auth/change-password": CacheConfig(skip_cache=True),

    # API documentation - long TTL
    "/docs": CacheConfig(
        ttl=86400,  # 24 hours
        vary_by=["Accept-Encoding"],
        max_size=10,
        compress=True
    ),
    "/redoc": CacheConfig(
        ttl=86400,  # 24 hours
        vary_by=["Accept-Encoding"],
        max_size=10,
        compress=True
    ),
    "/openapi.json": CacheConfig(
        ttl=86400,  # 24 hours
        vary_by=["Accept-Encoding"],
        max_size=10,
        compress=True
    ),

    # System endpoints
    "/system/status": CacheConfig(
        ttl=60,  # 1 minute
        vary_by=["Authorization"],
        max_size=10,
        compress=True,
        stale_while_revalidate=30
    ),
    "/system/metrics": CacheConfig(
        ttl=300,  # 5 minutes
        vary_by=["Authorization"],
        max_size=20,
        compress=True,
        stale_while_revalidate=60
    ),
    "/system/logs": CacheConfig(
        ttl=60,  # 1 minute
        vary_by=["Authorization"],
        max_size=50,
        compress=True,
        must_revalidate=True
    )
}

class CacheItem:
    def __init__(self, value: Any, expiry: float, config: CacheConfig):
        self.value = value
        self.expiry = expiry
        self.last_modified = time.time()
        self.etag = self._generate_etag(value)
        self.config = config

    def _generate_etag(self, value: Any) -> str:
        """Generate ETag for the cached value."""
        if isinstance(value, (dict, list)):
            value_str = json.dumps(value, sort_keys=True)
        else:
            value_str = str(value)
        return hashlib.md5(value_str.encode()).hexdigest()

    def is_expired(self) -> bool:
        """Check if the cache item has expired."""
        return time.time() > self.expiry

class LRUCache:
    def __init__(self, default_capacity: int = 1000):
        self.default_capacity = default_capacity
        self.caches: Dict[str, OrderedDict[str, CacheItem]] = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

    def _get_cache_for_path(self, path: str) -> OrderedDict[str, CacheItem]:
        """Get or create a cache for a specific path."""
        if path not in self.caches:
            config = CACHE_CONFIGS.get(path, CacheConfig())
            self.caches[path] = OrderedDict()
        return self.caches[path]

    def get(self, key: str, path: str) -> Optional[CacheItem]:
        """Get an item from the cache."""
        cache = self._get_cache_for_path(path)
        if key in cache:
            item = cache[key]
            if not item.is_expired():
                cache.move_to_end(key)
                self.stats["hits"] += 1
                return item
            else:
                del cache[key]
                self.stats["evictions"] += 1
        self.stats["misses"] += 1
        return None

    def set(self, key: str, value: Any, path: str, config: CacheConfig) -> None:
        """Set an item in the cache with TTL in seconds."""
        cache = self._get_cache_for_path(path)
        
        # Check cache size limit
        if len(cache) >= config.max_size:
            cache.popitem(last=False)
            self.stats["evictions"] += 1

        expiry = time.time() + config.ttl
        cache[key] = CacheItem(value, expiry, config)
        cache.move_to_end(key)

    def delete(self, key: str, path: str) -> None:
        """Delete an item from the cache."""
        cache = self._get_cache_for_path(path)
        if key in cache:
            del cache[key]

    def clear(self, path: Optional[str] = None) -> None:
        """Clear all items from the cache."""
        if path:
            if path in self.caches:
                self.caches[path].clear()
        else:
            for cache in self.caches.values():
                cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size = sum(len(cache) for cache in self.caches.values())
        return {
            **self.stats,
            "total_size": total_size,
            "caches": {
                path: len(cache) for path, cache in self.caches.items()
            }
        }

class CacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, cache: LRUCache):
        super().__init__(app)
        self.cache = cache

    async def dispatch(self, request: Request, call_next) -> Response:
        # Get cache config for the path
        path = request.url.path
        config = CACHE_CONFIGS.get(path, CacheConfig())

        # Skip caching if configured
        if config.skip_cache or config.no_store:
            return await call_next(request)

        # Skip caching for non-GET requests and certain paths
        if request.method != "GET" or path.startswith(("/docs", "/redoc", "/openapi.json")):
            return await call_next(request)

        # Generate cache key
        cache_key = self._generate_cache_key(request, config)
        
        # Check cache
        cached_item = self.cache.get(cache_key, path)
        if cached_item:
            # Check if the cached item is stale but can be used while revalidating
            if cached_item.is_expired() and config.stale_while_revalidate > 0:
                # Start revalidation in background
                self._revalidate_in_background(request, path, config)
                # Return stale response
                response = self._create_cached_response(cached_item, request)
                response.headers["X-Cache"] = "STALE"
                return response
            else:
                response = self._create_cached_response(cached_item, request)
                response.headers["X-Cache"] = "HIT"
                return response

        # Process request
        response = await call_next(request)
        
        # Cache response if successful
        if response.status_code == 200:
            self._cache_response(response, cache_key, path, config)
            response.headers["X-Cache"] = "MISS"
        
        return response

    def _generate_cache_key(self, request: Request, config: CacheConfig) -> str:
        """Generate a cache key based on the request and cache config."""
        key_parts = [request.url.path, request.url.query]
        
        # Add varying headers based on config
        for header in config.vary_by:
            key_parts.append(request.headers.get(header, ""))
        
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()

    def _create_cached_response(self, cached_item: CacheItem, request: Request) -> Response:
        """Create a response from cached data."""
        # Check conditional requests
        if_none_match = request.headers.get("If-None-Match")
        if_modified_since = request.headers.get("If-Modified-Since")

        if if_none_match and if_none_match == cached_item.etag:
            return Response(status_code=304)
        
        if if_modified_since:
            try:
                if_modified_since_time = time.strptime(if_modified_since, "%a, %d %b %Y %H:%M:%S GMT")
                if_modified_since_timestamp = time.mktime(if_modified_since_time)
                if cached_item.last_modified <= if_modified_since_timestamp:
                    return Response(status_code=304)
            except ValueError:
                pass

        # Create response with cached data
        response = Response(content=cached_item.value)
        
        # Set cache control headers based on config
        cache_control = []
        
        if cached_item.config.private:
            cache_control.append("private")
        else:
            cache_control.append("public")
            
        if cached_item.config.no_store:
            cache_control.append("no-store")
        else:
            cache_control.append(f"max-age={cached_item.config.ttl}")
            
        if cached_item.config.must_revalidate:
            cache_control.append("must-revalidate")
            
        if cached_item.config.stale_while_revalidate > 0:
            cache_control.append(f"stale-while-revalidate={cached_item.config.stale_while_revalidate}")
            
        response.headers["Cache-Control"] = ", ".join(cache_control)
        response.headers["ETag"] = cached_item.etag
        response.headers["Last-Modified"] = time.strftime(
            "%a, %d %b %Y %H:%M:%S GMT",
            time.gmtime(cached_item.last_modified)
        )
        
        return response

    def _cache_response(self, response: Response, cache_key: str, path: str, config: CacheConfig) -> None:
        """Cache the response data."""
        # Skip caching if no-store is set
        if config.no_store:
            return
            
        # Get response content
        content = response.body
        
        # Compress if configured
        if config.compress and "gzip" in response.headers.get("Content-Encoding", ""):
            content = gzip.compress(content)
        
        # Cache the response
        self.cache.set(cache_key, content, path, config)

    async def _revalidate_in_background(self, request: Request, path: str, config: CacheConfig) -> None:
        """Revalidate a stale cache entry in the background."""
        try:
            # Create a new request with the same parameters
            new_request = Request(scope=request.scope)
            # Process the request
            response = await self.app(new_request)
            # Update cache if successful
            if response.status_code == 200:
                cache_key = self._generate_cache_key(request, config)
                self._cache_response(response, cache_key, path, config)
        except Exception as e:
            logger.error(f"Error revalidating cache for {path}: {str(e)}")

# Initialize cache
cache = LRUCache()

def get_cache() -> LRUCache:
    """Get the cache instance."""
    return cache 

class CacheWarmupConfig:
    """Configuration for cache warming."""
    def __init__(
        self,
        enabled: bool = True,
        interval: int = 300,  # 5 minutes
        max_concurrent: int = 5,
        retry_attempts: int = 3,
        retry_delay: int = 5,  # seconds
        endpoints: List[Dict[str, Any]] = None,
        batch_size: int = 3,  # Number of endpoints to warm up in parallel
        timeout: int = 30,  # Request timeout in seconds
        max_retries: int = 3,  # Maximum number of retries per endpoint
        backoff_factor: float = 1.5  # Exponential backoff factor
    ):
        self.enabled = enabled
        self.interval = interval
        self.max_concurrent = max_concurrent
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.endpoints = endpoints or []
        self.batch_size = batch_size
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

# Define cache warming configurations for different endpoints
WARMUP_CONFIGS = {
    # High priority - Frequently accessed public data
    "/public/tax-rates": {
        "priority": 1,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 1800,  # 30 minutes
        "concurrent_requests": 1
    },
    "/public/deductions": {
        "priority": 1,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 1800,  # 30 minutes
        "concurrent_requests": 1
    },
    "/public/faq": {
        "priority": 1,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 3600,  # 1 hour
        "concurrent_requests": 1
    },

    # Medium priority - User interface components
    "/list/templates": {
        "priority": 2,
        "params": {"limit": 50, "sort": "popular"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 900,  # 15 minutes
        "concurrent_requests": 2
    },
    "/list/categories": {
        "priority": 2,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 1800,  # 30 minutes
        "concurrent_requests": 1
    },
    "/list/document-types": {
        "priority": 2,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 3600,  # 1 hour
        "concurrent_requests": 1
    },

    # API Documentation
    "/docs": {
        "priority": 3,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 7200,  # 2 hours
        "concurrent_requests": 1
    },
    "/redoc": {
        "priority": 3,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 7200,  # 2 hours
        "concurrent_requests": 1
    },
    "/openapi.json": {
        "priority": 3,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 7200,  # 2 hours
        "concurrent_requests": 1
    },

    # User interface components
    "/ui/components": {
        "priority": 2,
        "params": {"version": "latest"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 1800,  # 30 minutes
        "concurrent_requests": 2
    },
    "/ui/translations": {
        "priority": 2,
        "params": {"locale": "en"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 3600,  # 1 hour
        "concurrent_requests": 1
    },

    # Search and filtering
    "/search/suggestions": {
        "priority": 2,
        "params": {"limit": 10},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 900,  # 15 minutes
        "concurrent_requests": 2
    },
    "/search/filters": {
        "priority": 2,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 1800,  # 30 minutes
        "concurrent_requests": 1
    },

    # Public content
    "/public/updates": {
        "priority": 2,
        "params": {"limit": 5},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 900,  # 15 minutes
        "concurrent_requests": 1
    },
    "/public/announcements": {
        "priority": 2,
        "params": {"limit": 3},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 1800,  # 30 minutes
        "concurrent_requests": 1
    },
    "/public/help": {
        "priority": 2,
        "params": {"section": "general"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 3600,  # 1 hour
        "concurrent_requests": 1
    },

    # System status and metrics
    "/system/status": {
        "priority": 1,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 300,  # 5 minutes
        "concurrent_requests": 1
    },
    "/system/metrics": {
        "priority": 1,
        "params": {"period": "1h"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 600,  # 10 minutes
        "concurrent_requests": 1
    },

    # Document processing status
    "/process/status": {
        "priority": 1,
        "params": {"type": "all"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 300,  # 5 minutes
        "concurrent_requests": 2
    },
    "/process/queue": {
        "priority": 1,
        "params": {"limit": 10},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 300,  # 5 minutes
        "concurrent_requests": 1
    },

    # Analysis results
    "/analyze/summary": {
        "priority": 2,
        "params": {"type": "recent"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 900,  # 15 minutes
        "concurrent_requests": 2
    },
    "/analyze/trends": {
        "priority": 2,
        "params": {"period": "1d"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 1800,  # 30 minutes
        "concurrent_requests": 1
    },

    # Export templates
    "/export/templates": {
        "priority": 2,
        "params": {"type": "all"},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 3600,  # 1 hour
        "concurrent_requests": 1
    },
    "/export/formats": {
        "priority": 2,
        "params": {},
        "headers": {"Accept-Encoding": "gzip"},
        "warmup_interval": 7200,  # 2 hours
        "concurrent_requests": 1
    }
}

class CacheWarmup:
    """Handles cache warming for frequently accessed endpoints."""
    def __init__(self, app, cache: 'LRUCache', config: CacheWarmupConfig):
        self.app = app
        self.cache = cache
        self.config = config
        self.last_warmup: Dict[str, datetime] = {}
        self.warmup_stats: Dict[str, Dict[str, Any]] = {}
        self._warmup_task = None

    async def start(self):
        """Start the cache warming process."""
        if self.config.enabled:
            self._warmup_task = asyncio.create_task(self._warmup_loop())
            logger.info("Cache warming started")

    async def stop(self):
        """Stop the cache warming process."""
        if self._warmup_task:
            self._warmup_task.cancel()
            try:
                await self._warmup_task
            except asyncio.CancelledError:
                pass
            logger.info("Cache warming stopped")

    async def _warmup_loop(self):
        """Main warmup loop."""
        while True:
            try:
                await self._warmup_endpoints()
                await asyncio.sleep(self.config.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in warmup loop: {str(e)}")
                await asyncio.sleep(self.config.retry_delay)

    async def _warmup_endpoints(self):
        """Warm up all configured endpoints."""
        # Sort endpoints by priority
        endpoints = sorted(
            WARMUP_CONFIGS.items(),
            key=lambda x: x[1]["priority"]
        )

        # Process endpoints in batches
        for i in range(0, len(endpoints), self.config.max_concurrent):
            batch = endpoints[i:i + self.config.max_concurrent]
            tasks = [
                self._warmup_endpoint(path, config)
                for path, config in batch
            ]
            await asyncio.gather(*tasks)

    async def _warmup_endpoint(self, path: str, config: Dict[str, Any]):
        """Warm up a single endpoint."""
        try:
            # Check if endpoint needs warming
            last_warmup = self.last_warmup.get(path)
            if last_warmup and (datetime.now() - last_warmup).seconds < self.config.interval:
                return

            # Create request
            request = self._create_warmup_request(path, config)
            
            # Process request with retries
            for attempt in range(self.config.retry_attempts):
                try:
                    response = await self.app(request)
                    if response.status_code == 200:
                        # Update cache
                        cache_key = self.cache._generate_cache_key(request, CACHE_CONFIGS[path])
                        self.cache.set(
                            cache_key,
                            response.body,
                            path,
                            CACHE_CONFIGS[path]
                        )
                        
                        # Update stats
                        self._update_warmup_stats(path, True)
                        self.last_warmup[path] = datetime.now()
                        logger.info(f"Successfully warmed up {path}")
                        break
                except Exception as e:
                    if attempt == self.config.retry_attempts - 1:
                        self._update_warmup_stats(path, False, str(e))
                        logger.error(f"Failed to warm up {path}: {str(e)}")
                    else:
                        await asyncio.sleep(self.config.retry_delay)

        except Exception as e:
            logger.error(f"Error warming up {path}: {str(e)}")
            self._update_warmup_stats(path, False, str(e))

    def _create_warmup_request(self, path: str, config: Dict[str, Any]) -> Request:
        """Create a request for cache warming."""
        # Create query string from params
        query_string = "&".join(
            f"{k}={v}" for k, v in config["params"].items()
        )
        
        # Create request scope
        scope = {
            "type": "http",
            "method": "GET",
            "path": path,
            "query_string": query_string.encode() if query_string else b"",
            "headers": [
                (k.lower().encode(), v.encode())
                for k, v in config["headers"].items()
            ]
        }
        
        return Request(scope)

    def _update_warmup_stats(self, path: str, success: bool, error: str = None):
        """Update warmup statistics."""
        if path not in self.warmup_stats:
            self.warmup_stats[path] = {
                "total_attempts": 0,
                "successful_attempts": 0,
                "failed_attempts": 0,
                "last_error": None,
                "last_success": None,
                "last_attempt": None
            }
        
        stats = self.warmup_stats[path]
        stats["total_attempts"] += 1
        stats["last_attempt"] = datetime.now()
        
        if success:
            stats["successful_attempts"] += 1
            stats["last_success"] = datetime.now()
        else:
            stats["failed_attempts"] += 1
            stats["last_error"] = error

    def get_stats(self) -> Dict[str, Any]:
        """Get cache warming statistics."""
        return {
            "enabled": self.config.enabled,
            "interval": self.config.interval,
            "endpoints": {
                path: {
                    **stats,
                    "last_warmup": self.last_warmup.get(path)
                }
                for path, stats in self.warmup_stats.items()
            }
        }

# Initialize cache warmup
cache_warmup = None

def init_cache_warmup(app, cache: LRUCache) -> CacheWarmup:
    """Initialize cache warmup."""
    global cache_warmup
    config = CacheWarmupConfig(
        enabled=True,
        interval=300,  # 5 minutes
        max_concurrent=5,
        retry_attempts=3,
        retry_delay=5,
        endpoints=WARMUP_CONFIGS
    )
    cache_warmup = CacheWarmup(app, cache, config)
    return cache_warmup

def get_cache_warmup() -> Optional[CacheWarmup]:
    """Get the cache warmup instance."""
    return cache_warmup 