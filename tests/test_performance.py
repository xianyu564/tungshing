"""
Comprehensive performance and stress tests for TungShing.

This module tests performance characteristics, memory usage,
caching effectiveness, and scalability under various workloads.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import gc
import time
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pytest

from tungshing import TungShing
from tungshing.cache import get_cache_stats, clear_all_caches
from tungshing.memory_optimization import (
    get_memory_optimizer, optimize_memory, MemoryEfficientTungShing
)
from tungshing.profiling import profile_tungshing_creation, memory_benchmark


class TestPerformance:
    """Test performance characteristics of TungShing."""
    
    def setup_method(self):
        """Set up each test method."""
        clear_all_caches()
        gc.collect()
    
    def test_single_calculation_performance(self):
        """Test performance of single TungShing calculation."""
        dt = datetime(2025, 1, 1, 12, 0)
        
        # Time single calculation
        start_time = time.perf_counter()
        ts = TungShing(dt)
        creation_time = time.perf_counter() - start_time
        
        # Time property access
        start_time = time.perf_counter()
        year_char = ts.year8Char
        month_char = ts.month8Char
        day_char = ts.day8Char
        hour_char = ts.twohour8Char
        property_time = time.perf_counter() - start_time
        
        # Performance assertions
        assert creation_time < 0.1, f"Creation too slow: {creation_time:.3f}s"
        assert property_time < 0.05, f"Property access too slow: {property_time:.3f}s"
        
        # Verify results are correct
        assert isinstance(year_char, str)
        assert len(year_char) == 2
        assert isinstance(month_char, str)
        assert len(month_char) == 2
    
    def test_repeated_calculation_performance(self):
        """Test performance with repeated calculations (cache effectiveness)."""
        dt = datetime(2025, 1, 1, 12, 0)
        iterations = 100
        
        # First run (cold cache)
        start_time = time.perf_counter()
        for _ in range(iterations):
            ts = TungShing(dt)
            _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
        cold_time = time.perf_counter() - start_time
        
        # Second run (warm cache)
        start_time = time.perf_counter()
        for _ in range(iterations):
            ts = TungShing(dt)
            _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
        warm_time = time.perf_counter() - start_time
        
        # Cache should provide significant speedup
        speedup = cold_time / warm_time if warm_time > 0 else float('inf')
        assert speedup >= 1.5, f"Cache speedup insufficient: {speedup:.1f}x"
        
        # Verify cache usage
        stats = get_cache_stats()
        assert stats['total_size'] > 0, "Cache should contain entries"
    
    def test_different_dates_performance(self):
        """Test performance across different dates and edge cases."""
        # Test various challenging dates
        test_dates = [
            datetime(2025, 1, 1, 0, 0),      # New Year
            datetime(2025, 2, 4, 10, 42, 13),  # Near Lichun
            datetime(2025, 6, 21, 10, 42),   # Summer solstice
            datetime(2025, 12, 22, 9, 21),   # Winter solstice
            datetime(2025, 2, 28, 23, 59),   # Leap year edge
            datetime(1900, 1, 1, 12, 0),     # Start of supported range
            datetime(2099, 12, 31, 23, 59),  # End of supported range
        ]
        
        times = []
        for dt in test_dates:
            start_time = time.perf_counter()
            ts = TungShing(dt)
            _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
            times.append(time.perf_counter() - start_time)
        
        # All calculations should complete in reasonable time
        max_time = max(times)
        avg_time = sum(times) / len(times)
        
        assert max_time < 0.2, f"Slowest calculation too slow: {max_time:.3f}s"
        assert avg_time < 0.1, f"Average calculation too slow: {avg_time:.3f}s"
        
        # Verify variance is reasonable (no outliers)
        min_time = min(times)
        assert max_time / min_time < 10, "Performance variance too high"
    
    def test_timezone_performance(self):
        """Test performance impact of different timezones."""
        dt = datetime(2025, 1, 1, 12, 0)
        timezones = [
            'Asia/Shanghai',
            'Asia/Hong_Kong', 
            'Asia/Tokyo',
            'UTC',
            'America/New_York',
            'Europe/London'
        ]
        
        times = []
        for tz in timezones:
            start_time = time.perf_counter()
            ts = TungShing(dt, tz=tz, rule_tz=tz)
            _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
            times.append(time.perf_counter() - start_time)
        
        # Timezone handling shouldn't significantly impact performance
        max_time = max(times)
        min_time = min(times)
        
        assert max_time < 0.15, f"Timezone handling too slow: {max_time:.3f}s"
        assert max_time / min_time < 3, "Timezone performance variance too high"


class TestMemoryUsage:
    """Test memory usage and optimization."""
    
    def setup_method(self):
        """Set up each test method."""
        clear_all_caches()
        optimize_memory()
        gc.collect()
    
    def test_memory_efficient_tungshing(self):
        """Test memory-efficient TungShing wrapper."""
        dt = datetime(2025, 1, 1, 12, 0)
        
        # Create memory-efficient instance
        efficient_ts = MemoryEfficientTungShing(dt)
        
        # Test lazy evaluation
        initial_usage = efficient_ts.get_memory_usage()
        assert initial_usage['cache_count'] == 0, "Should start with empty cache"
        
        # Access properties
        year_char = efficient_ts.year8Char
        month_char = efficient_ts.month8Char
        
        # Check cache growth
        after_usage = efficient_ts.get_memory_usage()
        assert after_usage['cache_count'] > initial_usage['cache_count'], "Cache should grow"
        
        # Verify results are correct
        regular_ts = TungShing(dt)
        assert year_char == regular_ts.year8Char
        assert month_char == regular_ts.month8Char
    
    def test_memory_growth_under_load(self):
        """Test memory usage under heavy load."""
        optimizer = get_memory_optimizer()
        
        # Get baseline memory stats
        baseline_stats = optimizer.get_memory_stats()
        
        # Create many TungShing objects
        objects = []
        for i in range(100):
            dt = datetime(2025, 1, 1) + timedelta(days=i)
            ts = TungShing(dt)
            _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
            objects.append(ts)
        
        # Check memory growth
        loaded_stats = optimizer.get_memory_stats()
        memory_growth = loaded_stats.memory_bytes - baseline_stats.memory_bytes
        
        # Memory growth should be reasonable
        assert memory_growth < 50 * 1024 * 1024, f"Memory growth too high: {memory_growth / 1024 / 1024:.1f}MB"
        
        # Clear objects and optimize
        objects.clear()
        optimization_result = optimizer.optimize_memory()
        
        # Memory should be reclaimed
        assert optimization_result['gc_collected'] >= 0, "Garbage collection should run"
        
        final_stats = optimizer.get_memory_stats()
        memory_reclaimed = loaded_stats.memory_bytes - final_stats.memory_bytes
        
        # Some memory should be reclaimed (allowing for some overhead)
        assert memory_reclaimed >= 0, "Some memory should be reclaimed"
    
    def test_cache_memory_management(self):
        """Test cache memory management under pressure."""
        # Fill cache with many entries
        for i in range(1000):
            dt = datetime(2025, 1, 1) + timedelta(hours=i)
            ts = TungShing(dt)
            _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
        
        # Check cache stats
        stats = get_cache_stats()
        assert stats['total_size'] > 100, "Cache should contain many entries"
        
        # Trigger memory optimization
        optimization_result = optimize_memory()
        
        # Cache should be managed (may be cleared or reduced)
        new_stats = get_cache_stats()
        assert new_stats['total_size'] <= stats['total_size'], "Cache size should not increase"


class TestConcurrency:
    """Test concurrent access and thread safety."""
    
    def test_concurrent_calculations(self):
        """Test concurrent TungShing calculations."""
        num_threads = 10
        calculations_per_thread = 20
        
        def worker_thread(thread_id):
            """Worker function for concurrent testing."""
            results = []
            for i in range(calculations_per_thread):
                dt = datetime(2025, 1, 1) + timedelta(days=thread_id, hours=i)
                ts = TungShing(dt)
                result = (ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char)
                results.append(result)
            return results
        
        # Run concurrent calculations
        start_time = time.perf_counter()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_thread, i) for i in range(num_threads)]
            all_results = []
            for future in as_completed(futures):
                all_results.extend(future.result())
        
        concurrent_time = time.perf_counter() - start_time
        
        # Verify all results
        assert len(all_results) == num_threads * calculations_per_thread
        for result in all_results:
            assert len(result) == 4  # year, month, day, hour
            assert all(isinstance(char, str) and len(char) == 2 for char in result)
        
        # Concurrent execution should be reasonably fast
        expected_sequential_time = (num_threads * calculations_per_thread) * 0.01  # 10ms per calc
        assert concurrent_time < expected_sequential_time * 2, "Concurrent performance poor"
    
    def test_cache_thread_safety(self):
        """Test cache thread safety under concurrent access."""
        num_threads = 5
        same_date = datetime(2025, 1, 1, 12, 0)
        
        def cache_stress_worker():
            """Worker that stresses the cache with same calculations."""
            for _ in range(50):
                ts = TungShing(same_date)
                _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
        
        # Run concurrent cache access
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(cache_stress_worker) for _ in range(num_threads)]
            for future in as_completed(futures):
                future.result()  # Wait for completion
        
        # Verify cache is consistent
        stats = get_cache_stats()
        assert stats['total_size'] > 0, "Cache should contain entries"
        
        # Verify results are still correct
        ts = TungShing(same_date)
        result = (ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char)
        assert all(isinstance(char, str) and len(char) == 2 for char in result)


class TestStress:
    """Stress tests for TungShing under extreme conditions."""
    
    def test_large_date_range_stress(self):
        """Test calculations across a large date range."""
        start_date = datetime(1900, 1, 1)
        end_date = datetime(2099, 12, 31)
        
        # Test sampling across full range
        sample_count = 100
        date_range = (end_date - start_date).days
        sample_interval = date_range // sample_count
        
        start_time = time.perf_counter()
        
        for i in range(sample_count):
            sample_date = start_date + timedelta(days=i * sample_interval)
            ts = TungShing(sample_date)
            result = (ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char)
            
            # Verify result format
            assert all(isinstance(char, str) and len(char) == 2 for char in result)
        
        total_time = time.perf_counter() - start_time
        avg_time = total_time / sample_count
        
        # Should handle full range efficiently
        assert avg_time < 0.05, f"Average calculation too slow: {avg_time:.3f}s"
        assert total_time < 10, f"Total time too high: {total_time:.1f}s"
    
    def test_rapid_successive_calculations(self):
        """Test rapid successive calculations."""
        base_date = datetime(2025, 1, 1)
        num_calculations = 1000
        
        start_time = time.perf_counter()
        
        for i in range(num_calculations):
            # Vary date slightly for each calculation
            dt = base_date + timedelta(seconds=i)
            ts = TungShing(dt)
            _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
        
        total_time = time.perf_counter() - start_time
        avg_time = total_time / num_calculations
        
        # Should handle rapid calculations efficiently
        assert avg_time < 0.002, f"Average calculation too slow: {avg_time:.4f}s"
        assert total_time < 5, f"Total time too high: {total_time:.1f}s"
    
    def test_memory_stress(self):
        """Test memory usage under stress conditions."""
        # Create many objects without keeping references
        initial_memory = get_memory_optimizer().get_memory_stats().memory_bytes
        
        for batch in range(10):
            objects = []
            for i in range(100):
                dt = datetime(2025, 1, 1) + timedelta(days=batch * 100 + i)
                ts = TungShing(dt)
                _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
                objects.append(ts)
            
            # Clear batch
            objects.clear()
            
            # Periodic cleanup
            if batch % 3 == 0:
                gc.collect()
        
        # Final cleanup
        optimize_memory()
        final_memory = get_memory_optimizer().get_memory_stats().memory_bytes
        
        # Memory usage should not grow unbounded
        memory_growth = final_memory - initial_memory
        assert memory_growth < 100 * 1024 * 1024, f"Memory growth too high: {memory_growth / 1024 / 1024:.1f}MB"


class TestBenchmarks:
    """Comprehensive benchmarks for performance analysis."""
    
    def test_comprehensive_benchmark(self):
        """Run comprehensive performance benchmark."""
        # Use profiling utilities
        test_dates = [
            datetime(2025, 1, 1, 12, 0),
            datetime(2025, 2, 4, 10, 42, 13),
            datetime(2025, 6, 21, 10, 42),
            datetime(2025, 12, 22, 9, 21),
        ]
        
        # Run benchmark
        results = profile_tungshing_creation(iterations=50, dates=test_dates)
        
        # Verify benchmark results structure
        assert 'operations' in results
        assert 'summary' in results
        assert 'bottlenecks' in results
        
        # Check that all operations were tested
        operations = results['operations']
        expected_ops = ['instantiation', 'year8Char', 'month8Char', 'day8Char', 'twohour8Char']
        for op in expected_ops:
            assert op in operations, f"Missing operation: {op}"
            assert operations[op]['avg_time'] > 0, f"Invalid timing for {op}"
        
        # Performance should be reasonable
        summary = results['summary']
        assert summary['avg_time_per_operation'] < 0.05, "Average operation time too high"
        
        # Should identify bottlenecks
        bottlenecks = results['bottlenecks']
        assert len(bottlenecks) > 0, "Should identify some bottlenecks"
        assert sum(b['percentage'] for b in bottlenecks) <= 100, "Bottleneck percentages invalid"
    
    def test_memory_benchmark(self):
        """Run memory usage benchmark."""
        # Run memory benchmark
        results = memory_benchmark(duration=2.0)
        
        # Verify results structure
        assert 'snapshots' in results
        assert 'peak_usage' in results
        assert 'average_usage' in results
        assert 'gc_stats' in results
        
        # Should have collected memory snapshots
        assert len(results['snapshots']) > 0, "Should have memory snapshots"
        
        # Memory values should be reasonable
        assert results['peak_usage'] > 0, "Peak usage should be positive"
        assert results['average_usage'] > 0, "Average usage should be positive"
        assert results['peak_usage'] >= results['average_usage'], "Peak should be >= average"


@pytest.mark.slow
class TestLongRunning:
    """Long-running performance tests (marked as slow)."""
    
    def test_extended_memory_monitoring(self):
        """Extended memory monitoring test."""
        # Run longer memory benchmark
        results = memory_benchmark(duration=10.0)
        
        # Should detect any memory leaks over longer period
        snapshots = results['snapshots']
        if len(snapshots) > 20:
            early_memory = sum(s['memory_rss'] for s in snapshots[:10]) / 10
            late_memory = sum(s['memory_rss'] for s in snapshots[-10:]) / 10
            
            # Memory growth should be bounded
            growth_ratio = late_memory / early_memory if early_memory > 0 else 1
            assert growth_ratio < 1.5, f"Potential memory leak detected: {growth_ratio:.2f}x growth"
    
    def test_sustained_load(self):
        """Test sustained load over extended period."""
        duration = 30  # seconds
        start_time = time.time()
        calculation_count = 0
        
        while time.time() - start_time < duration:
            # Create varied calculations
            dt = datetime(2025, 1, 1) + timedelta(seconds=calculation_count)
            ts = TungShing(dt)
            _ = ts.year8Char, ts.month8Char, ts.day8Char, ts.twohour8Char
            
            calculation_count += 1
            
            # Periodic cleanup
            if calculation_count % 100 == 0:
                gc.collect()
        
        # Calculate performance metrics
        total_time = time.time() - start_time
        calculations_per_second = calculation_count / total_time
        
        # Should maintain reasonable performance under sustained load
        assert calculations_per_second > 50, f"Sustained performance too low: {calculations_per_second:.1f} calc/s"
        
        # Memory should be stable
        final_stats = get_memory_optimizer().get_memory_stats()
        assert final_stats.memory_bytes < 500 * 1024 * 1024, "Memory usage too high after sustained load"


if __name__ == "__main__":
    # Run basic performance tests when executed directly
    print("Running basic performance tests...")
    
    test_perf = TestPerformance()
    test_perf.setup_method()
    test_perf.test_single_calculation_performance()
    print("✓ Single calculation performance")
    
    test_perf.test_repeated_calculation_performance()
    print("✓ Repeated calculation performance")
    
    test_mem = TestMemoryUsage()
    test_mem.setup_method()
    test_mem.test_memory_efficient_tungshing()
    print("✓ Memory efficient TungShing")
    
    test_bench = TestBenchmarks()
    test_bench.test_comprehensive_benchmark()
    print("✓ Comprehensive benchmark")
    
    print("\nAll basic performance tests passed!")
    print("\nRun with pytest for full test suite:")
    print("  pytest tests/test_performance.py -v")
    print("  pytest tests/test_performance.py -v -m slow  # for long-running tests")