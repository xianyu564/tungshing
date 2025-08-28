# TungShing Performance Optimization Guide

This document provides comprehensive guidance on optimizing TungShing performance for various use cases, from simple calculations to high-throughput applications.

## 📊 Performance Overview

TungShing is designed for high performance with multiple optimization layers:

- **Intelligent Caching**: Automatic caching of expensive calculations
- **Memory Optimization**: Advanced memory management and object pooling
- **Lazy Evaluation**: Deferred computation until values are needed
- **Concurrent Safety**: Thread-safe operations for multi-threaded applications

## 🚀 Quick Performance Tips

### 1. Use Caching Effectively

```python
from tungshing import TungShing
from datetime import datetime

# Good: Reuse calculations for same dates
dt = datetime(2025, 1, 1, 12, 0)
ts = TungShing(dt)

# Multiple property accesses are cached
year = ts.year8Char
month = ts.month8Char
day = ts.day8Char
hour = ts.twohour8Char
```

### 2. Memory-Efficient Usage

```python
from tungshing.memory_optimization import MemoryEfficientTungShing

# For memory-sensitive applications
efficient_ts = MemoryEfficientTungShing(datetime.now())
year = efficient_ts.year8Char  # Lazy evaluation

# Clear cache when done
efficient_ts.clear_cache()
```

### 3. Batch Processing

```python
from tungshing import TungShing
from tungshing.cache import clear_all_caches
from datetime import datetime, timedelta

def process_date_range(start_date, days):
    results = []
    
    # Process in batches to manage memory
    batch_size = 100
    for i in range(0, days, batch_size):
        batch_results = []
        
        for j in range(min(batch_size, days - i)):
            dt = start_date + timedelta(days=i + j)
            ts = TungShing(dt)
            batch_results.append({
                'date': dt,
                'year': ts.year8Char,
                'month': ts.month8Char,
                'day': ts.day8Char,
                'hour': ts.twohour8Char
            })
        
        results.extend(batch_results)
        
        # Periodic cleanup
        if i % (batch_size * 10) == 0:
            clear_all_caches()
    
    return results
```

## 🔧 Advanced Optimization Techniques

### Memory Optimization

```python
from tungshing.memory_optimization import get_memory_optimizer, optimize_memory

# Get memory statistics
optimizer = get_memory_optimizer()
stats = optimizer.get_memory_stats()
print(f"Memory usage: {stats.memory_bytes / 1024 / 1024:.1f} MB")

# Optimize memory usage
optimization_result = optimize_memory()
print(f"Memory freed: {optimization_result['memory_freed'] / 1024 / 1024:.1f} MB")

# Generate detailed report
report = optimizer.get_optimization_report()
print(report)
```

### Performance Profiling

```python
from tungshing.profiling import get_profiler, profile_tungshing_creation

# Profile specific operations
profiler = get_profiler()

with profiler.profile_block("calculation"):
    ts = TungShing(datetime.now())
    result = ts.year8Char

# Generate performance report
report = profiler.generate_report()
print(report)

# Benchmark multiple dates
benchmark_results = profile_tungshing_creation(
    iterations=100,
    dates=[datetime(2025, 1, 1), datetime(2025, 6, 21)]
)
```

### Custom Caching Strategies

```python
from tungshing.cache import _global_cache

# Configure cache size
_global_cache.max_size = 5000  # Increase for high-throughput apps

# Monitor cache effectiveness
stats = _global_cache.get_stats()
print(f"Cache hit ratio: {stats['total_accesses'] / max(stats['size'], 1):.2f}")

# Clear cache when needed
_global_cache.clear()
```

## 🏗️ Architecture Best Practices

### 1. Application Design Patterns

#### Singleton Pattern for Shared Cache
```python
class TungShingManager:
    """Singleton manager for TungShing operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._cache = {}
            self._initialized = True
    
    def get_tungshing(self, dt, tz="Asia/Shanghai"):
        key = (dt.isoformat(), tz)
        if key not in self._cache:
            self._cache[key] = TungShing(dt, tz=tz)
        return self._cache[key]

# Usage
manager = TungShingManager()
ts = manager.get_tungshing(datetime.now())
```

#### Factory Pattern for Configuration
```python
class TungShingFactory:
    """Factory for creating optimized TungShing instances."""
    
    def __init__(self, default_tz="Asia/Shanghai", use_memory_optimization=True):
        self.default_tz = default_tz
        self.use_memory_optimization = use_memory_optimization
    
    def create(self, dt=None, tz=None):
        tz = tz or self.default_tz
        dt = dt or datetime.now()
        
        if self.use_memory_optimization:
            from tungshing.memory_optimization import MemoryEfficientTungShing
            return MemoryEfficientTungShing(dt, tz=tz)
        else:
            return TungShing(dt, tz=tz)

# Usage
factory = TungShingFactory(use_memory_optimization=True)
ts = factory.create(datetime.now())
```

### 2. Concurrent Applications

```python
import threading
from concurrent.futures import ThreadPoolExecutor
from tungshing import TungShing

class ThreadSafeTungShingProcessor:
    """Thread-safe TungShing processor for concurrent applications."""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self._local = threading.local()
    
    def process_dates(self, dates):
        """Process multiple dates concurrently."""
        
        def process_single_date(dt):
            # Each thread gets its own TungShing instance
            if not hasattr(self._local, 'tungshing_cache'):
                self._local.tungshing_cache = {}
            
            key = dt.isoformat()
            if key not in self._local.tungshing_cache:
                self._local.tungshing_cache[key] = TungShing(dt)
            
            ts = self._local.tungshing_cache[key]
            return {
                'date': dt,
                'year': ts.year8Char,
                'month': ts.month8Char,
                'day': ts.day8Char,
                'hour': ts.twohour8Char
            }
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(process_single_date, dates))
        
        return results

# Usage
processor = ThreadSafeTungShingProcessor(max_workers=8)
dates = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(100)]
results = processor.process_dates(dates)
```

### 3. Web Application Integration

#### Flask Example
```python
from flask import Flask, jsonify, request
from tungshing import TungShing
from tungshing.cache import get_cache_stats
from datetime import datetime

app = Flask(__name__)

@app.route('/tungshing')
def get_tungshing():
    # Parse date parameter
    date_str = request.args.get('date')
    if date_str:
        dt = datetime.fromisoformat(date_str)
    else:
        dt = datetime.now()
    
    # Get timezone parameter
    tz = request.args.get('tz', 'Asia/Shanghai')
    
    # Calculate TungShing
    ts = TungShing(dt, tz=tz)
    
    return jsonify({
        'date': dt.isoformat(),
        'timezone': tz,
        'year_pillar': ts.year8Char,
        'month_pillar': ts.month8Char,
        'day_pillar': ts.day8Char,
        'hour_pillar': ts.twohour8Char,
        'lunar_year': ts.lunarYear,
        'lunar_month': ts.lunarMonth,
        'lunar_day': ts.lunarDay
    })

@app.route('/cache-stats')
def cache_stats():
    return jsonify(get_cache_stats())
```

#### Django Example
```python
from django.http import JsonResponse
from django.views import View
from tungshing import TungShing
from tungshing.memory_optimization import get_memory_optimizer
from datetime import datetime

class TungShingView(View):
    def get(self, request):
        # Parse parameters
        date_str = request.GET.get('date')
        tz = request.GET.get('tz', 'Asia/Shanghai')
        
        if date_str:
            dt = datetime.fromisoformat(date_str)
        else:
            dt = datetime.now()
        
        # Calculate TungShing
        ts = TungShing(dt, tz=tz)
        
        return JsonResponse({
            'date': dt.isoformat(),
            'timezone': tz,
            'four_pillars': {
                'year': ts.year8Char,
                'month': ts.month8Char,
                'day': ts.day8Char,
                'hour': ts.twohour8Char
            },
            'lunar_calendar': {
                'year': ts.lunarYear,
                'month': ts.lunarMonth,
                'day': ts.lunarDay
            }
        })

class PerformanceView(View):
    def get(self, request):
        optimizer = get_memory_optimizer()
        stats = optimizer.get_memory_stats()
        
        return JsonResponse({
            'memory_usage_mb': stats.memory_bytes / 1024 / 1024,
            'cache_entries': stats.cache_size,
            'total_objects': stats.total_objects
        })
```

## 📈 Performance Monitoring

### Application Metrics

```python
import time
from contextlib import contextmanager
from tungshing import TungShing

class PerformanceMonitor:
    """Monitor TungShing performance in production."""
    
    def __init__(self):
        self.metrics = {
            'calculation_count': 0,
            'total_time': 0,
            'error_count': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    @contextmanager
    def measure_calculation(self):
        start_time = time.perf_counter()
        try:
            yield
            self.metrics['calculation_count'] += 1
        except Exception:
            self.metrics['error_count'] += 1
            raise
        finally:
            self.metrics['total_time'] += time.perf_counter() - start_time
    
    def get_stats(self):
        if self.metrics['calculation_count'] > 0:
            avg_time = self.metrics['total_time'] / self.metrics['calculation_count']
        else:
            avg_time = 0
        
        return {
            'calculations': self.metrics['calculation_count'],
            'errors': self.metrics['error_count'],
            'average_time': avg_time,
            'total_time': self.metrics['total_time']
        }

# Usage
monitor = PerformanceMonitor()

with monitor.measure_calculation():
    ts = TungShing(datetime.now())
    result = ts.year8Char

print(monitor.get_stats())
```

### Health Checks

```python
from tungshing import TungShing
from tungshing.cache import get_cache_stats
from tungshing.memory_optimization import get_memory_optimizer
from datetime import datetime

def health_check():
    """Comprehensive health check for TungShing performance."""
    
    health = {
        'status': 'healthy',
        'issues': [],
        'metrics': {}
    }
    
    try:
        # Test basic functionality
        start_time = time.perf_counter()
        ts = TungShing(datetime.now())
        result = ts.year8Char
        calc_time = time.perf_counter() - start_time
        
        health['metrics']['calculation_time'] = calc_time
        
        if calc_time > 0.1:  # 100ms threshold
            health['issues'].append(f"Slow calculation: {calc_time:.3f}s")
        
        # Check cache health
        cache_stats = get_cache_stats()
        health['metrics']['cache_size'] = cache_stats['total_size']
        
        if cache_stats['total_size'] > 10000:
            health['issues'].append(f"Large cache: {cache_stats['total_size']} entries")
        
        # Check memory usage
        memory_stats = get_memory_optimizer().get_memory_stats()
        memory_mb = memory_stats.memory_bytes / 1024 / 1024
        health['metrics']['memory_mb'] = memory_mb
        
        if memory_mb > 500:  # 500MB threshold
            health['issues'].append(f"High memory usage: {memory_mb:.1f}MB")
        
        # Set overall status
        if health['issues']:
            health['status'] = 'warning'
        
    except Exception as e:
        health['status'] = 'error'
        health['issues'].append(f"Calculation failed: {str(e)}")
    
    return health

# Usage
health = health_check()
print(f"Status: {health['status']}")
if health['issues']:
    for issue in health['issues']:
        print(f"⚠️  {issue}")
```

## 🎯 Use Case Specific Optimizations

### High-Frequency Trading Applications
```python
from tungshing import TungShing
from tungshing.memory_optimization import MemoryEfficientTungShing
import asyncio

class HighFrequencyTungShing:
    """Optimized for high-frequency calculations."""
    
    def __init__(self):
        # Pre-warm cache with common dates
        self._prewarm_cache()
    
    def _prewarm_cache(self):
        """Pre-warm cache with likely dates."""
        base_date = datetime.now()
        for i in range(-30, 31):  # ±30 days
            dt = base_date + timedelta(days=i)
            ts = TungShing(dt)
            _ = ts.year8Char, ts.month8Char, ts.day8Char
    
    async def calculate_async(self, dt):
        """Async calculation for high concurrency."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._calculate, dt)
    
    def _calculate(self, dt):
        ts = MemoryEfficientTungShing(dt)
        return {
            'year': ts.year8Char,
            'month': ts.month8Char,
            'day': ts.day8Char,
            'hour': ts.twohour8Char
        }
```

### Data Analysis and Batch Processing
```python
import pandas as pd
from tungshing import TungShing
from multiprocessing import Pool

def process_dataframe(df, date_column='date', tz='Asia/Shanghai'):
    """Add TungShing columns to pandas DataFrame."""
    
    def calculate_pillars(date_str):
        dt = pd.to_datetime(date_str)
        ts = TungShing(dt, tz=tz)
        return pd.Series({
            'year_pillar': ts.year8Char,
            'month_pillar': ts.month8Char,
            'day_pillar': ts.day8Char,
            'hour_pillar': ts.twohour8Char
        })
    
    # Apply TungShing calculations
    pillars_df = df[date_column].apply(calculate_pillars)
    
    # Concatenate results
    result_df = pd.concat([df, pillars_df], axis=1)
    return result_df

# Usage with large datasets
# df = pd.read_csv('large_dataset.csv')
# result = process_dataframe(df, date_column='timestamp')
```

### Microservices Architecture
```python
from tungshing import TungShing
from tungshing.cache import get_cache_stats, clear_all_caches
import time
import logging

class TungShingMicroservice:
    """Microservice wrapper for TungShing."""
    
    def __init__(self, cache_cleanup_interval=3600):  # 1 hour
        self.cache_cleanup_interval = cache_cleanup_interval
        self.last_cleanup = time.time()
        self.request_count = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def calculate(self, dt, tz="Asia/Shanghai"):
        """Main calculation method with monitoring."""
        self.request_count += 1
        
        start_time = time.perf_counter()
        try:
            ts = TungShing(dt, tz=tz)
            result = {
                'date': dt.isoformat(),
                'timezone': tz,
                'four_pillars': {
                    'year': ts.year8Char,
                    'month': ts.month8Char,
                    'day': ts.day8Char,
                    'hour': ts.twohour8Char
                },
                'lunar_calendar': {
                    'year': ts.lunarYear,
                    'month': ts.lunarMonth,
                    'day': ts.lunarDay
                }
            }
            
            calc_time = time.perf_counter() - start_time
            self.logger.info(f"Calculation completed in {calc_time:.3f}s")
            
            # Periodic cleanup
            self._maybe_cleanup()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Calculation failed: {str(e)}")
            raise
    
    def _maybe_cleanup(self):
        """Periodic cache cleanup."""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cache_cleanup_interval:
            stats_before = get_cache_stats()
            clear_all_caches()
            stats_after = get_cache_stats()
            
            self.logger.info(
                f"Cache cleanup: {stats_before['total_size']} -> "
                f"{stats_after['total_size']} entries"
            )
            
            self.last_cleanup = current_time
    
    def get_health(self):
        """Service health information."""
        stats = get_cache_stats()
        return {
            'status': 'healthy',
            'requests_processed': self.request_count,
            'cache_entries': stats['total_size'],
            'uptime_seconds': time.time() - (self.last_cleanup - self.cache_cleanup_interval)
        }
```

## 🔍 Debugging Performance Issues

### Common Performance Problems

1. **Memory Leaks**
   ```python
   # Monitor memory growth
   from tungshing.memory_optimization import get_memory_optimizer
   
   optimizer = get_memory_optimizer()
   initial_memory = optimizer.get_memory_stats().memory_bytes
   
   # ... run your application ...
   
   final_memory = optimizer.get_memory_stats().memory_bytes
   growth = final_memory - initial_memory
   
   if growth > 100 * 1024 * 1024:  # 100MB
       print(f"Potential memory leak: {growth / 1024 / 1024:.1f}MB growth")
   ```

2. **Cache Inefficiency**
   ```python
   from tungshing.cache import get_cache_stats
   
   stats = get_cache_stats()
   hit_ratio = stats['total_accesses'] / max(stats['size'], 1)
   
   if hit_ratio < 2.0:  # Less than 2 hits per cache entry
       print("Poor cache efficiency - consider different caching strategy")
   ```

3. **Slow Calculations**
   ```python
   from tungshing.profiling import get_profiler
   
   profiler = get_profiler()
   with profiler.profile_block("slow_calculation"):
       # Your slow code here
       pass
   
   suggestions = profiler.get_optimization_suggestions()
   for suggestion in suggestions:
       print(f"💡 {suggestion}")
   ```

## 📋 Performance Checklist

### Development Phase
- [ ] Use appropriate caching strategy for your use case
- [ ] Implement proper error handling and validation
- [ ] Consider memory-efficient alternatives for high-volume applications
- [ ] Add performance monitoring and logging
- [ ] Write performance tests for critical paths

### Testing Phase
- [ ] Run performance benchmarks
- [ ] Test memory usage under load
- [ ] Verify thread safety for concurrent applications
- [ ] Test with realistic data volumes
- [ ] Profile critical code paths

### Production Phase
- [ ] Monitor calculation times and memory usage
- [ ] Set up alerts for performance degradation
- [ ] Implement health checks
- [ ] Plan for cache cleanup and memory optimization
- [ ] Monitor error rates and cache hit ratios

### Scaling Phase
- [ ] Consider horizontal scaling strategies
- [ ] Implement load balancing for multiple instances
- [ ] Optimize for your specific hardware and network
- [ ] Consider caching strategies across service boundaries
- [ ] Plan for database integration if storing results

## 🎓 Advanced Topics

For more advanced optimization techniques, see:

- **Algorithmic Optimizations**: Custom calculation algorithms for specific use cases
- **Hardware Optimization**: GPU acceleration for massive parallel calculations
- **Distributed Computing**: Scaling across multiple servers and cloud services
- **Integration Patterns**: Best practices for integrating with existing systems

## 📞 Getting Help

If you encounter performance issues:

1. Check the [performance test suite](../tests/test_performance.py) for examples
2. Use the built-in profiling tools to identify bottlenecks
3. Review the memory optimization utilities
4. Consider your specific use case requirements
5. Open an issue with performance profiling data if needed

Remember: Premature optimization is the root of all evil. Profile first, optimize based on data, and always measure the impact of your changes.