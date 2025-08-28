"""
Advanced memory optimization and algorithmic improvements for TungShing.

This module implements sophisticated memory management techniques,
algorithmic optimizations, and performance improvements to minimize
memory footprint and maximize calculation speed.
"""
from __future__ import annotations

import gc
import weakref
from collections import OrderedDict
from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import sys
import threading
from dataclasses import dataclass


@dataclass
class MemoryStats:
    """Memory usage statistics."""
    total_objects: int
    cache_size: int
    weak_refs: int
    memory_bytes: int
    largest_objects: List[Tuple[str, int]]


class AdaptiveCache:
    """
    Adaptive cache that automatically adjusts size based on memory pressure.
    
    Features:
    - Dynamic size adjustment based on available memory
    - Priority-based eviction (LRU with frequency weighting)
    - Memory pressure detection and automatic cleanup
    - Thread-safe operations
    """
    
    def __init__(self, initial_size: int = 1000, max_size: int = 10000):
        """
        Initialize adaptive cache.
        
        Args:
            initial_size: Starting cache size
            max_size: Maximum cache size
        """
        self.initial_size = initial_size
        self.max_size = max_size
        self.current_max = initial_size
        
        # Thread-safe storage
        self._lock = threading.RLock()
        self._data: OrderedDict = OrderedDict()
        self._frequencies: Dict[str, int] = {}
        self._last_access: Dict[str, float] = {}
        
        # Memory monitoring
        self._memory_checks = 0
        self._last_cleanup = 0
        
    def _calculate_priority(self, key: str) -> float:
        """
        Calculate priority score for cache entry.
        Higher score = higher priority = less likely to be evicted.
        
        Args:
            key: Cache key
            
        Returns:
            Priority score (higher is better)
        """
        import time
        
        frequency = self._frequencies.get(key, 1)
        last_access = self._last_access.get(key, 0)
        time_since_access = time.time() - last_access
        
        # Combine frequency and recency
        # Recent + frequent = high priority
        priority = frequency / (1 + time_since_access / 3600)  # Decay over hours
        return priority
    
    def _check_memory_pressure(self) -> bool:
        """
        Check if system is under memory pressure.
        
        Returns:
            True if memory pressure detected
        """
        self._memory_checks += 1
        
        # Only check every 100 operations to avoid overhead
        if self._memory_checks % 100 != 0:
            return False
        
        try:
            import psutil
            memory = psutil.virtual_memory()
            # Consider pressure if >85% memory used
            return memory.percent > 85
        except ImportError:
            # Fallback: check cache size vs configured limits
            return len(self._data) > self.current_max * 0.9
    
    def _adaptive_resize(self) -> None:
        """Adaptively resize cache based on memory conditions."""
        if self._check_memory_pressure():
            # Reduce cache size under pressure
            new_size = max(self.initial_size, int(self.current_max * 0.8))
            if new_size < self.current_max:
                self.current_max = new_size
                self._evict_to_size(new_size)
        else:
            # Grow cache if memory is available
            new_size = min(self.max_size, int(self.current_max * 1.1))
            if new_size > self.current_max:
                self.current_max = new_size
    
    def _evict_to_size(self, target_size: int) -> None:
        """
        Evict items to reach target size using priority-based LRU.
        
        Args:
            target_size: Target cache size
        """
        if len(self._data) <= target_size:
            return
        
        # Calculate priorities for all items
        priorities = [(key, self._calculate_priority(key)) for key in self._data]
        # Sort by priority (ascending = evict first)
        priorities.sort(key=lambda x: x[1])
        
        # Remove lowest priority items
        items_to_remove = len(self._data) - target_size
        for i in range(items_to_remove):
            key = priorities[i][0]
            del self._data[key]
            self._frequencies.pop(key, None)
            self._last_access.pop(key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache with frequency tracking.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        with self._lock:
            if key in self._data:
                # Update access tracking
                import time
                self._frequencies[key] = self._frequencies.get(key, 0) + 1
                self._last_access[key] = time.time()
                
                # Move to end (most recently used)
                value = self._data.pop(key)
                self._data[key] = value
                
                return value
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set item in cache with adaptive resizing.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            import time
            
            # Update tracking
            self._frequencies[key] = self._frequencies.get(key, 0) + 1
            self._last_access[key] = time.time()
            
            # Add/update item
            if key in self._data:
                del self._data[key]  # Remove old position
            self._data[key] = value
            
            # Adaptive resizing
            self._adaptive_resize()
            
            # Evict if needed
            if len(self._data) > self.current_max:
                self._evict_to_size(self.current_max)
    
    def clear(self) -> None:
        """Clear all cache data."""
        with self._lock:
            self._data.clear()
            self._frequencies.clear()
            self._last_access.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_frequency = sum(self._frequencies.values())
            avg_frequency = total_frequency / len(self._frequencies) if self._frequencies else 0
            
            return {
                'size': len(self._data),
                'max_size': self.current_max,
                'configured_max': self.max_size,
                'total_accesses': total_frequency,
                'avg_frequency': avg_frequency,
                'memory_checks': self._memory_checks
            }


class ObjectPool:
    """
    Object pool for reusing expensive-to-create objects.
    
    Reduces memory allocation overhead for frequently created
    objects like datetime calculations and intermediate results.
    """
    
    def __init__(self, factory_func: callable, max_size: int = 100):
        """
        Initialize object pool.
        
        Args:
            factory_func: Function to create new objects
            max_size: Maximum pool size
        """
        self.factory_func = factory_func
        self.max_size = max_size
        self._pool: List[Any] = []
        self._lock = threading.Lock()
        self._created_count = 0
        self._reused_count = 0
    
    def acquire(self, *args, **kwargs) -> Any:
        """
        Acquire an object from the pool.
        
        Args:
            *args, **kwargs: Arguments for object creation/initialization
            
        Returns:
            Object instance
        """
        with self._lock:
            if self._pool:
                obj = self._pool.pop()
                self._reused_count += 1
                # Reset/initialize the object if it has a reset method
                if hasattr(obj, 'reset'):
                    obj.reset(*args, **kwargs)
                return obj
            else:
                self._created_count += 1
                return self.factory_func(*args, **kwargs)
    
    def release(self, obj: Any) -> None:
        """
        Release an object back to the pool.
        
        Args:
            obj: Object to release
        """
        with self._lock:
            if len(self._pool) < self.max_size:
                # Clean the object if it has a clean method
                if hasattr(obj, 'clean'):
                    obj.clean()
                self._pool.append(obj)
    
    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics."""
        with self._lock:
            return {
                'pool_size': len(self._pool),
                'max_size': self.max_size,
                'created': self._created_count,
                'reused': self._reused_count,
                'reuse_ratio': self._reused_count / (self._created_count + self._reused_count) if (self._created_count + self._reused_count) > 0 else 0
            }


class LazyCalculator:
    """
    Lazy evaluation system for expensive calculations.
    
    Defers calculations until actually needed and caches results
    to avoid redundant computations.
    """
    
    def __init__(self):
        """Initialize lazy calculator."""
        self._calculations: Dict[str, callable] = {}
        self._cache: Dict[str, Any] = {}
        self._dependencies: Dict[str, Set[str]] = {}
        self._invalidated: Set[str] = set()
    
    def register_calculation(self, name: str, func: callable, dependencies: Optional[List[str]] = None) -> None:
        """
        Register a lazy calculation.
        
        Args:
            name: Calculation identifier
            func: Function to perform calculation
            dependencies: List of other calculations this depends on
        """
        self._calculations[name] = func
        self._dependencies[name] = set(dependencies or [])
    
    def invalidate(self, name: str) -> None:
        """
        Invalidate a calculation and all dependent calculations.
        
        Args:
            name: Calculation to invalidate
        """
        self._invalidated.add(name)
        self._cache.pop(name, None)
        
        # Invalidate dependent calculations
        for calc_name, deps in self._dependencies.items():
            if name in deps:
                self.invalidate(calc_name)
    
    def calculate(self, name: str, *args, **kwargs) -> Any:
        """
        Get calculation result, computing if necessary.
        
        Args:
            name: Calculation identifier
            *args, **kwargs: Arguments for calculation
            
        Returns:
            Calculation result
        """
        cache_key = f"{name}_{hash((args, tuple(sorted(kwargs.items()))))}"
        
        # Return cached result if available and not invalidated
        if cache_key in self._cache and name not in self._invalidated:
            return self._cache[cache_key]
        
        # Calculate dependencies first
        for dep_name in self._dependencies.get(name, []):
            if dep_name in self._calculations:
                self.calculate(dep_name, *args, **kwargs)
        
        # Perform calculation
        if name in self._calculations:
            result = self._calculations[name](*args, **kwargs)
            self._cache[cache_key] = result
            self._invalidated.discard(name)
            return result
        else:
            raise ValueError(f"Unknown calculation: {name}")
    
    def clear_cache(self) -> None:
        """Clear all cached calculations."""
        self._cache.clear()
        self._invalidated.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get calculator statistics."""
        return {
            'registered_calculations': len(self._calculations),
            'cached_results': len(self._cache),
            'invalidated_count': len(self._invalidated),
            'dependency_count': sum(len(deps) for deps in self._dependencies.values())
        }


class MemoryOptimizer:
    """
    Comprehensive memory optimization manager.
    
    Coordinates various memory optimization techniques and
    provides monitoring and automatic cleanup capabilities.
    """
    
    def __init__(self):
        """Initialize memory optimizer."""
        self.adaptive_cache = AdaptiveCache()
        self.object_pools: Dict[str, ObjectPool] = {}
        self.lazy_calculator = LazyCalculator()
        
        # Weak reference tracking
        self._tracked_objects: Set[weakref.ref] = set()
        self._cleanup_threshold = 1000
        
    def create_object_pool(self, name: str, factory_func: callable, max_size: int = 100) -> ObjectPool:
        """
        Create a named object pool.
        
        Args:
            name: Pool identifier
            factory_func: Function to create objects
            max_size: Maximum pool size
            
        Returns:
            Object pool instance
        """
        pool = ObjectPool(factory_func, max_size)
        self.object_pools[name] = pool
        return pool
    
    def track_object(self, obj: Any) -> None:
        """
        Track an object for memory monitoring.
        
        Args:
            obj: Object to track
        """
        def cleanup_callback(ref):
            self._tracked_objects.discard(ref)
        
        ref = weakref.ref(obj, cleanup_callback)
        self._tracked_objects.add(ref)
        
        # Periodic cleanup
        if len(self._tracked_objects) > self._cleanup_threshold:
            self._cleanup_dead_references()
    
    def _cleanup_dead_references(self) -> None:
        """Clean up dead weak references."""
        dead_refs = {ref for ref in self._tracked_objects if ref() is None}
        self._tracked_objects -= dead_refs
    
    def optimize_memory(self) -> Dict[str, Any]:
        """
        Perform comprehensive memory optimization.
        
        Returns:
            Optimization results and statistics
        """
        stats_before = self.get_memory_stats()
        
        # Force garbage collection
        collected = gc.collect()
        
        # Clear adaptive cache if under memory pressure
        try:
            import psutil
            memory = psutil.virtual_memory()
            if memory.percent > 80:  # 80% memory usage threshold
                old_cache_size = len(self.adaptive_cache._data)
                self.adaptive_cache.clear()
                cache_freed = old_cache_size
            else:
                cache_freed = 0
        except ImportError:
            # Fallback: clear cache if it's large
            if len(self.adaptive_cache._data) > 5000:
                cache_freed = len(self.adaptive_cache._data)
                self.adaptive_cache.clear()
            else:
                cache_freed = 0
        
        # Clear lazy calculator cache
        calc_cache_size = len(self.lazy_calculator._cache)
        self.lazy_calculator.clear_cache()
        
        # Clean up dead references
        old_ref_count = len(self._tracked_objects)
        self._cleanup_dead_references()
        refs_freed = old_ref_count - len(self._tracked_objects)
        
        stats_after = self.get_memory_stats()
        
        return {
            'gc_collected': collected,
            'cache_entries_freed': cache_freed,
            'calc_cache_freed': calc_cache_size,
            'dead_refs_freed': refs_freed,
            'memory_before': stats_before.memory_bytes,
            'memory_after': stats_after.memory_bytes,
            'memory_freed': stats_before.memory_bytes - stats_after.memory_bytes
        }
    
    def get_memory_stats(self) -> MemoryStats:
        """
        Get comprehensive memory usage statistics.
        
        Returns:
            Memory statistics
        """
        # Count objects
        all_objects = gc.get_objects()
        total_objects = len(all_objects)
        
        # Cache sizes
        cache_size = len(self.adaptive_cache._data)
        
        # Weak references
        weak_refs = len(self._tracked_objects)
        
        # Memory usage
        try:
            import psutil
            process = psutil.Process()
            memory_bytes = process.memory_info().rss
        except ImportError:
            # Fallback: use sys.getsizeof for approximate memory
            memory_bytes = sum(sys.getsizeof(obj) for obj in all_objects[:1000])  # Sample only
        
        # Find largest objects
        largest_objects = []
        try:
            object_sizes = []
            for obj in all_objects[:1000]:  # Sample to avoid performance impact
                try:
                    size = sys.getsizeof(obj)
                    if size > 1024:  # Only include objects > 1KB
                        object_sizes.append((type(obj).__name__, size))
                except (TypeError, AttributeError):
                    continue
            
            # Sort by size and take top 10
            object_sizes.sort(key=lambda x: x[1], reverse=True)
            largest_objects = object_sizes[:10]
        except Exception:
            # Fallback if object inspection fails
            largest_objects = [("unknown", 0)]
        
        return MemoryStats(
            total_objects=total_objects,
            cache_size=cache_size,
            weak_refs=weak_refs,
            memory_bytes=memory_bytes,
            largest_objects=largest_objects
        )
    
    def get_optimization_report(self) -> str:
        """
        Generate a comprehensive memory optimization report.
        
        Returns:
            Formatted report string
        """
        stats = self.get_memory_stats()
        cache_stats = self.adaptive_cache.get_stats()
        
        lines = []
        lines.append("=" * 60)
        lines.append("Memory Optimization Report")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("")
        
        lines.append("📊 Memory Statistics:")
        lines.append(f"  Total objects: {stats.total_objects:,}")
        lines.append(f"  Memory usage: {stats.memory_bytes / 1024 / 1024:.1f} MB")
        lines.append(f"  Cache entries: {stats.cache_size:,}")
        lines.append(f"  Tracked references: {stats.weak_refs:,}")
        lines.append("")
        
        lines.append("🔧 Cache Performance:")
        lines.append(f"  Current size: {cache_stats['size']:,}")
        lines.append(f"  Max size: {cache_stats['max_size']:,}")
        lines.append(f"  Total accesses: {cache_stats['total_accesses']:,}")
        lines.append(f"  Average frequency: {cache_stats['avg_frequency']:.2f}")
        lines.append("")
        
        lines.append("🏆 Largest Objects:")
        for obj_type, size in stats.largest_objects[:5]:
            lines.append(f"  {obj_type}: {size / 1024:.1f} KB")
        lines.append("")
        
        # Object pool statistics
        if self.object_pools:
            lines.append("🔄 Object Pools:")
            for name, pool in self.object_pools.items():
                pool_stats = pool.get_stats()
                lines.append(f"  {name}:")
                lines.append(f"    Reuse ratio: {pool_stats['reuse_ratio']:.2%}")
                lines.append(f"    Pool size: {pool_stats['pool_size']}/{pool_stats['max_size']}")
        
        # Lazy calculator statistics
        calc_stats = self.lazy_calculator.get_stats()
        if calc_stats['registered_calculations'] > 0:
            lines.append("")
            lines.append("⚡ Lazy Calculator:")
            lines.append(f"  Registered calculations: {calc_stats['registered_calculations']}")
            lines.append(f"  Cached results: {calc_stats['cached_results']}")
            lines.append(f"  Dependencies: {calc_stats['dependency_count']}")
        
        return "\n".join(lines)


# Global memory optimizer instance
_global_memory_optimizer = MemoryOptimizer()


def get_memory_optimizer() -> MemoryOptimizer:
    """Get the global memory optimizer instance."""
    return _global_memory_optimizer


def optimize_memory() -> Dict[str, Any]:
    """
    Convenience function for memory optimization.
    
    Returns:
        Optimization results
    """
    return _global_memory_optimizer.optimize_memory()


def get_memory_report() -> str:
    """
    Convenience function to get memory optimization report.
    
    Returns:
        Formatted memory report
    """
    return _global_memory_optimizer.get_optimization_report()


def create_object_pool(name: str, factory_func: callable, max_size: int = 100) -> ObjectPool:
    """
    Convenience function to create an object pool.
    
    Args:
        name: Pool identifier
        factory_func: Function to create objects
        max_size: Maximum pool size
        
    Returns:
        Object pool instance
    """
    return _global_memory_optimizer.create_object_pool(name, factory_func, max_size)


class MemoryEfficientTungShing:
    """
    Memory-optimized wrapper for TungShing calculations.
    
    Implements various memory optimization techniques:
    - Lazy evaluation of expensive properties
    - Weak reference caching
    - Object pooling for temporary objects
    - Adaptive cache sizing
    """
    
    def __init__(self, dt: Optional[datetime] = None, tz: str = "Asia/Shanghai", rule_tz: str = "Asia/Shanghai"):
        """
        Initialize memory-efficient TungShing.
        
        Args:
            dt: DateTime object (uses current time if None)
            tz: Output timezone
            rule_tz: Calculation timezone
        """
        self._dt = dt or datetime.now()
        self._tz = tz
        self._rule_tz = rule_tz
        
        # Lazy evaluation cache
        self._computed: Dict[str, Any] = {}
        self._computing: Set[str] = set()  # Prevent circular calculations
        
        # Track this instance for memory monitoring
        _global_memory_optimizer.track_object(self)
    
    def _lazy_compute(self, property_name: str, compute_func: callable) -> Any:
        """
        Lazy computation with caching and circular dependency protection.
        
        Args:
            property_name: Name of the property being computed
            compute_func: Function to compute the property
            
        Returns:
            Computed value
        """
        if property_name in self._computed:
            return self._computed[property_name]
        
        if property_name in self._computing:
            raise RuntimeError(f"Circular dependency detected in {property_name}")
        
        self._computing.add(property_name)
        try:
            result = compute_func()
            self._computed[property_name] = result
            return result
        finally:
            self._computing.discard(property_name)
    
    @property
    def tungshing_instance(self) -> Any:
        """Get the underlying TungShing instance with caching."""
        def compute():
            from .core import TungShing
            return TungShing(self._dt, tz=self._tz, rule_tz=self._rule_tz)
        
        return self._lazy_compute('_tungshing', compute)
    
    @property
    def year8Char(self) -> str:
        """Lazy computation of year pillar."""
        return self._lazy_compute('year8Char', lambda: self.tungshing_instance.year8Char)
    
    @property
    def month8Char(self) -> str:
        """Lazy computation of month pillar."""
        return self._lazy_compute('month8Char', lambda: self.tungshing_instance.month8Char)
    
    @property
    def day8Char(self) -> str:
        """Lazy computation of day pillar.""" 
        return self._lazy_compute('day8Char', lambda: self.tungshing_instance.day8Char)
    
    @property
    def twohour8Char(self) -> str:
        """Lazy computation of hour pillar."""
        return self._lazy_compute('twohour8Char', lambda: self.tungshing_instance.twohour8Char)
    
    def clear_cache(self) -> None:
        """Clear all cached computations."""
        self._computed.clear()
        self._computing.clear()
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics for this instance."""
        total_size = sys.getsizeof(self)
        
        cache_size = sum(sys.getsizeof(v) for v in self._computed.values())
        cache_count = len(self._computed)
        
        return {
            'total_size': total_size,
            'cache_size': cache_size,
            'cache_count': cache_count,
            'cache_ratio': cache_size / total_size if total_size > 0 else 0
        }