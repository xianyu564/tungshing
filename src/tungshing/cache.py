"""
Performance optimization module with intelligent caching for TungShing.

This module provides advanced caching mechanisms to significantly improve
performance for repeated calculations, especially for solar terms and
expensive astronomical computations.
"""
from __future__ import annotations

import functools
import hashlib
from datetime import datetime, date
from typing import Any, Callable, Dict, Optional, Tuple
from weakref import WeakKeyDictionary


class PerformanceCache:
    """
    High-performance cache optimized for TungShing calculations.
    
    Features:
    - LRU cache for solar term calculations
    - Weak reference cache for object instances
    - Intelligent cache invalidation
    - Memory-efficient storage
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize performance cache.
        
        Args:
            max_size: Maximum number of cached items
        """
        self.max_size = max_size
        self._solar_term_cache: Dict[str, Any] = {}
        self._ganzhi_cache: Dict[str, str] = {}
        self._lunar_cache: Dict[str, Any] = {}
        self._access_order: list = []
        
    def _evict_if_needed(self) -> None:
        """Remove oldest items if cache exceeds max size."""
        while len(self._access_order) > self.max_size:
            oldest_key = self._access_order.pop(0)
            self._solar_term_cache.pop(oldest_key, None)
            self._ganzhi_cache.pop(oldest_key, None)
            self._lunar_cache.pop(oldest_key, None)
    
    def _make_cache_key(self, *args, **kwargs) -> str:
        """Create a stable cache key from arguments."""
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_solar_term(self, year: int, month: int, day: int, rule_tz: str) -> Optional[Any]:
        """Get cached solar term data."""
        key = self._make_cache_key(year, month, day, rule_tz)
        if key in self._solar_term_cache:
            # Move to end (most recently used)
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
            return self._solar_term_cache[key]
        return None
    
    def set_solar_term(self, year: int, month: int, day: int, rule_tz: str, value: Any) -> None:
        """Cache solar term data."""
        key = self._make_cache_key(year, month, day, rule_tz)
        self._solar_term_cache[key] = value
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        self._evict_if_needed()
    
    def get_ganzhi(self, year: int, month: int, day: int) -> Optional[str]:
        """Get cached Ganzhi calculation."""
        key = self._make_cache_key(year, month, day)
        return self._ganzhi_cache.get(key)
    
    def set_ganzhi(self, year: int, month: int, day: int, value: str) -> None:
        """Cache Ganzhi calculation."""
        key = self._make_cache_key(year, month, day)
        self._ganzhi_cache[key] = value
        self._evict_if_needed()
    
    def clear(self) -> None:
        """Clear all cached data."""
        self._solar_term_cache.clear()
        self._ganzhi_cache.clear()
        self._lunar_cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            'solar_terms': len(self._solar_term_cache),
            'ganzhi': len(self._ganzhi_cache),
            'lunar': len(self._lunar_cache),
            'total_size': len(self._access_order),
            'max_size': self.max_size
        }


# Global cache instance
_global_cache = PerformanceCache()


def cached_solar_term(func: Callable) -> Callable:
    """
    Decorator for caching expensive solar term calculations.
    
    Automatically caches results based on function arguments,
    significantly improving performance for repeated calculations.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Use global cache for solar term calculations
        if len(args) >= 4:  # year, month, day, rule_tz
            cached_result = _global_cache.get_solar_term(*args[:4])
            if cached_result is not None:
                return cached_result
        
        # Calculate and cache result
        result = func(*args, **kwargs)
        if len(args) >= 4:
            _global_cache.set_solar_term(*args[:4], result)
        
        return result
    
    return wrapper


def cached_ganzhi(func: Callable) -> Callable:
    """
    Decorator for caching Ganzhi calculations.
    
    Caches stem-branch combinations for faster repeated access.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract date components for caching
        if len(args) >= 3:  # year, month, day
            cached_result = _global_cache.get_ganzhi(*args[:3])
            if cached_result is not None:
                return cached_result
        
        # Calculate and cache result
        result = func(*args, **kwargs)
        if len(args) >= 3:
            _global_cache.set_ganzhi(*args[:3], result)
        
        return result
    
    return wrapper


class InstanceCache:
    """
    Weak reference cache for TungShing instances.
    
    Prevents duplicate calculations for the same datetime,
    while allowing garbage collection when references are released.
    """
    
    def __init__(self):
        self._cache: WeakKeyDictionary = WeakKeyDictionary()
    
    def get_or_create(self, cls, *args, **kwargs):
        """Get cached instance or create new one."""
        # Create a cache key from arguments
        cache_key = self._make_key(*args, **kwargs)
        
        # Check if we have a cached instance
        for cached_args, instance in self._cache.items():
            if cached_args == cache_key:
                return instance
        
        # Create new instance and cache it
        instance = cls(*args, **kwargs)
        self._cache[cache_key] = instance
        return instance
    
    def _make_key(self, *args, **kwargs) -> Tuple:
        """Create a hashable cache key."""
        key_parts = []
        for arg in args:
            if isinstance(arg, datetime):
                key_parts.append(arg.isoformat())
            else:
                key_parts.append(str(arg))
        
        for k, v in sorted(kwargs.items()):
            if isinstance(v, datetime):
                key_parts.append(f"{k}={v.isoformat()}")
            else:
                key_parts.append(f"{k}={v}")
        
        return tuple(key_parts)


# Global instance cache
_instance_cache = InstanceCache()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get comprehensive cache statistics.
    
    Returns:
        Dict with cache performance metrics and usage statistics.
    """
    stats = _global_cache.get_stats()
    stats['instance_cache_size'] = len(_instance_cache._cache)
    return stats


def clear_all_caches() -> None:
    """Clear all caches to free memory."""
    _global_cache.clear()
    _instance_cache._cache.clear()


def optimize_memory() -> Dict[str, int]:
    """
    Optimize memory usage by clearing old cache entries.
    
    Returns:
        Dict with memory optimization statistics.
    """
    old_stats = get_cache_stats()
    
    # Clear caches that are getting too large
    if old_stats['total_size'] > old_stats['max_size'] * 0.8:
        _global_cache._evict_if_needed()
    
    new_stats = get_cache_stats()
    
    return {
        'freed_solar_terms': old_stats['solar_terms'] - new_stats['solar_terms'],
        'freed_ganzhi': old_stats['ganzhi'] - new_stats['ganzhi'],
        'total_freed': old_stats['total_size'] - new_stats['total_size']
    }