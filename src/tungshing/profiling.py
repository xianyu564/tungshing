"""
Advanced profiling and debugging tools for TungShing.

This module provides comprehensive performance profiling, memory analysis,
and debugging utilities to optimize TungShing performance and identify
bottlenecks in calculations.
"""
from __future__ import annotations

import cProfile
import functools
import io
import pstats
import time
import tracemalloc
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple
import sys
import gc
import psutil
import os


class PerformanceProfiler:
    """
    Advanced performance profiler for TungShing calculations.
    
    Provides detailed timing analysis, memory profiling, and
    bottleneck identification for optimization purposes.
    """
    
    def __init__(self):
        """Initialize profiler."""
        self.profiles: Dict[str, Any] = {}
        self.memory_snapshots: List[Any] = []
        self.timing_data: Dict[str, List[float]] = {}
        
    @contextmanager
    def profile_block(self, name: str):
        """
        Profile a code block with detailed timing and memory analysis.
        
        Args:
            name: Identifier for this profiling session
            
        Example:
            >>> profiler = PerformanceProfiler()
            >>> with profiler.profile_block("calculation"):
            ...     ts = TungShing(datetime.now())
            ...     result = ts.year8Char
        """
        # Start memory tracking
        tracemalloc.start()
        start_memory = tracemalloc.get_traced_memory()
        
        # Start CPU profiling
        pr = cProfile.Profile()
        pr.enable()
        
        # Record start time
        start_time = time.perf_counter()
        start_process_time = time.process_time()
        
        try:
            yield
        finally:
            # Record end time
            end_time = time.perf_counter()
            end_process_time = time.process_time()
            
            # Stop CPU profiling
            pr.disable()
            
            # Get memory usage
            end_memory = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Store results
            self.profiles[name] = {
                'profiler': pr,
                'wall_time': end_time - start_time,
                'cpu_time': end_process_time - start_process_time,
                'memory_start': start_memory,
                'memory_end': end_memory,
                'memory_peak': end_memory[1],
                'memory_delta': end_memory[0] - start_memory[0]
            }
    
    def profile_function(self, iterations: int = 100):
        """
        Decorator for comprehensive function profiling.
        
        Args:
            iterations: Number of iterations to run for statistical analysis
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                times = []
                memory_usage = []
                
                for i in range(iterations):
                    # Memory snapshot before
                    gc.collect()
                    process = psutil.Process()
                    mem_before = process.memory_info().rss
                    
                    # Time the function
                    start = time.perf_counter()
                    result = func(*args, **kwargs)
                    end = time.perf_counter()
                    
                    # Memory snapshot after
                    mem_after = process.memory_info().rss
                    
                    times.append(end - start)
                    memory_usage.append(mem_after - mem_before)
                
                # Statistical analysis
                func_name = func.__name__
                if func_name not in self.timing_data:
                    self.timing_data[func_name] = []
                
                self.timing_data[func_name].extend(times)
                
                # Store detailed statistics
                self.profiles[f"{func_name}_stats"] = {
                    'iterations': iterations,
                    'min_time': min(times),
                    'max_time': max(times),
                    'avg_time': sum(times) / len(times),
                    'total_time': sum(times),
                    'avg_memory': sum(memory_usage) / len(memory_usage),
                    'max_memory': max(memory_usage),
                    'times': times,
                    'memory_usage': memory_usage
                }
                
                return result
            
            return wrapper
        return decorator
    
    def benchmark_tungshing_operations(self, test_dates: Optional[List[datetime]] = None) -> Dict[str, Any]:
        """
        Comprehensive benchmark of TungShing operations.
        
        Args:
            test_dates: List of dates to test (uses defaults if None)
            
        Returns:
            Dictionary with detailed benchmark results
        """
        from .core import TungShing
        
        if test_dates is None:
            test_dates = [
                datetime(2025, 1, 1, 12, 0),
                datetime(2025, 2, 4, 10, 42, 13),  # Near Lichun
                datetime(2025, 6, 21, 10, 42),     # Summer solstice
                datetime(2025, 12, 22, 9, 21),     # Winter solstice
                datetime(2024, 12, 31, 23, 59),    # Edge case
            ]
        
        results = {
            'operations': {},
            'summary': {},
            'memory_analysis': {},
            'bottlenecks': []
        }
        
        # Test each operation
        operations = [
            'instantiation',
            'year8Char',
            'month8Char', 
            'day8Char',
            'twohour8Char',
            'lunarYear',
            'lunarMonth',
            'lunarDay'
        ]
        
        for op_name in operations:
            op_times = []
            op_memory = []
            
            for dt in test_dates:
                # Memory before
                gc.collect()
                process = psutil.Process()
                mem_before = process.memory_info().rss
                
                # Time the operation
                start = time.perf_counter()
                
                if op_name == 'instantiation':
                    ts = TungShing(dt)
                else:
                    ts = TungShing(dt)
                    _ = getattr(ts, op_name)
                
                end = time.perf_counter()
                
                # Memory after
                mem_after = process.memory_info().rss
                
                op_times.append(end - start)
                op_memory.append(mem_after - mem_before)
            
            # Statistical analysis
            results['operations'][op_name] = {
                'avg_time': sum(op_times) / len(op_times),
                'min_time': min(op_times),
                'max_time': max(op_times),
                'total_time': sum(op_times),
                'avg_memory': sum(op_memory) / len(op_memory),
                'times': op_times,
                'memory': op_memory
            }
        
        # Overall summary
        total_time = sum(results['operations'][op]['total_time'] for op in operations)
        avg_time_per_op = total_time / len(operations)
        
        results['summary'] = {
            'total_time': total_time,
            'avg_time_per_operation': avg_time_per_op,
            'test_dates_count': len(test_dates),
            'operations_count': len(operations)
        }
        
        # Identify bottlenecks
        op_times = [(op, data['avg_time']) for op, data in results['operations'].items()]
        op_times.sort(key=lambda x: x[1], reverse=True)
        
        results['bottlenecks'] = [
            {
                'operation': op,
                'avg_time': time_val,
                'percentage': (time_val / total_time) * 100
            }
            for op, time_val in op_times[:3]  # Top 3 slowest
        ]
        
        return results
    
    def memory_usage_analysis(self, test_duration: float = 10.0) -> Dict[str, Any]:
        """
        Analyze memory usage patterns over time.
        
        Args:
            test_duration: Duration in seconds to monitor
            
        Returns:
            Memory usage analysis results
        """
        from .core import TungShing
        
        results = {
            'snapshots': [],
            'peak_usage': 0,
            'average_usage': 0,
            'memory_leaks': [],
            'gc_stats': {}
        }
        
        start_time = time.time()
        process = psutil.Process()
        
        # Baseline memory
        gc.collect()
        baseline_memory = process.memory_info().rss
        
        # Monitor memory usage
        while time.time() - start_time < test_duration:
            # Create some TungShing objects
            dates = [
                datetime.now(),
                datetime.now() + timedelta(days=1),
                datetime.now() - timedelta(days=1)
            ]
            
            for dt in dates:
                ts = TungShing(dt)
                _ = ts.year8Char, ts.month8Char, ts.day8Char
            
            # Record memory usage
            current_memory = process.memory_info().rss
            results['snapshots'].append({
                'timestamp': time.time() - start_time,
                'memory_rss': current_memory,
                'memory_vms': process.memory_info().vms,
                'delta_from_baseline': current_memory - baseline_memory
            })
            
            time.sleep(0.1)  # Sample every 100ms
        
        # Analysis
        if results['snapshots']:
            memory_values = [s['memory_rss'] for s in results['snapshots']]
            results['peak_usage'] = max(memory_values)
            results['average_usage'] = sum(memory_values) / len(memory_values)
            
            # Detect potential memory leaks (consistently increasing memory)
            if len(memory_values) > 10:
                recent_avg = sum(memory_values[-10:]) / 10
                early_avg = sum(memory_values[:10]) / 10
                
                if recent_avg > early_avg * 1.1:  # 10% increase
                    results['memory_leaks'].append({
                        'type': 'potential_leak',
                        'early_avg': early_avg,
                        'recent_avg': recent_avg,
                        'increase_percentage': (recent_avg - early_avg) / early_avg * 100
                    })
        
        # GC statistics
        results['gc_stats'] = {
            'collections': gc.get_stats(),
            'objects': len(gc.get_objects())
        }
        
        return results
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate a comprehensive performance report.
        
        Args:
            output_file: Optional file path to save the report
            
        Returns:
            Report text content
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("TungShing Performance Analysis Report")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated: {datetime.now().isoformat()}")
        report_lines.append("")
        
        # Profile summaries
        if self.profiles:
            report_lines.append("📊 Profile Summaries:")
            report_lines.append("-" * 40)
            
            for name, data in self.profiles.items():
                if 'wall_time' in data:
                    report_lines.append(f"  {name}:")
                    report_lines.append(f"    Wall time: {data['wall_time']:.4f}s")
                    report_lines.append(f"    CPU time:  {data['cpu_time']:.4f}s")
                    report_lines.append(f"    Memory delta: {data['memory_delta']:,} bytes")
                    report_lines.append(f"    Memory peak:  {data['memory_peak']:,} bytes")
                    report_lines.append("")
        
        # Timing statistics
        if self.timing_data:
            report_lines.append("⏱️  Timing Statistics:")
            report_lines.append("-" * 40)
            
            for func_name, times in self.timing_data.items():
                if times:
                    avg_time = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    report_lines.append(f"  {func_name}:")
                    report_lines.append(f"    Calls: {len(times)}")
                    report_lines.append(f"    Average: {avg_time:.4f}s")
                    report_lines.append(f"    Min: {min_time:.4f}s")
                    report_lines.append(f"    Max: {max_time:.4f}s")
                    report_lines.append("")
        
        # Detailed profiling data
        for name, data in self.profiles.items():
            if 'profiler' in data:
                report_lines.append(f"🔍 Detailed Profile: {name}")
                report_lines.append("-" * 40)
                
                # Create string buffer for profile output
                s = io.StringIO()
                ps = pstats.Stats(data['profiler'], stream=s)
                ps.sort_stats('cumulative')
                ps.print_stats(20)  # Top 20 functions
                
                profile_output = s.getvalue()
                report_lines.append(profile_output)
                report_lines.append("")
        
        report_text = "\n".join(report_lines)
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text
    
    def get_optimization_suggestions(self) -> List[str]:
        """
        Analyze profiling data and provide optimization suggestions.
        
        Returns:
            List of actionable optimization recommendations
        """
        suggestions = []
        
        # Analyze timing data
        if self.timing_data:
            for func_name, times in self.timing_data.items():
                if times:
                    avg_time = sum(times) / len(times)
                    max_time = max(times)
                    
                    # Suggest caching for slow functions
                    if avg_time > 0.01:  # 10ms threshold
                        suggestions.append(
                            f"Consider caching results for {func_name} "
                            f"(avg: {avg_time:.3f}s, max: {max_time:.3f}s)"
                        )
                    
                    # Suggest optimization for highly variable functions
                    min_time = min(times)
                    if max_time > min_time * 5:  # High variance
                        suggestions.append(
                            f"High performance variance in {func_name} "
                            f"(min: {min_time:.3f}s, max: {max_time:.3f}s) - "
                            f"investigate conditional branches"
                        )
        
        # Analyze memory usage
        for name, data in self.profiles.items():
            if 'memory_delta' in data and data['memory_delta'] > 1024 * 1024:  # 1MB
                suggestions.append(
                    f"High memory usage in {name} "
                    f"({data['memory_delta'] / 1024 / 1024:.1f}MB) - "
                    f"consider memory optimization"
                )
        
        # Generic suggestions if no specific issues found
        if not suggestions:
            suggestions.extend([
                "Performance is generally good, consider adding more caching for frequently accessed data",
                "Monitor memory usage during long-running operations",
                "Consider using lazy evaluation for expensive calculations"
            ])
        
        return suggestions


class DebugTracer:
    """
    Advanced debugging and tracing utilities for TungShing.
    
    Provides detailed execution tracing, state inspection,
    and debugging helpers for complex calculations.
    """
    
    def __init__(self):
        """Initialize debug tracer."""
        self.trace_data: List[Dict[str, Any]] = []
        self.enabled = False
        
    def enable_tracing(self) -> None:
        """Enable execution tracing."""
        self.enabled = True
        self.trace_data.clear()
        
    def disable_tracing(self) -> None:
        """Disable execution tracing."""
        self.enabled = False
        
    def trace_call(self, func_name: str, args: tuple, kwargs: dict, result: Any = None) -> None:
        """
        Record a function call for debugging.
        
        Args:
            func_name: Name of the function being called
            args: Positional arguments
            kwargs: Keyword arguments
            result: Function result (if available)
        """
        if not self.enabled:
            return
            
        self.trace_data.append({
            'timestamp': time.time(),
            'function': func_name,
            'args': str(args)[:200],  # Truncate long arguments
            'kwargs': str(kwargs)[:200],
            'result': str(result)[:100] if result is not None else None,
            'stack_depth': len(traceback.extract_stack())
        })
    
    def trace_decorator(self, func: Callable) -> Callable:
        """
        Decorator to automatically trace function calls.
        
        Args:
            func: Function to trace
            
        Returns:
            Wrapped function with tracing
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if self.enabled:
                self.trace_call(func.__name__, args, kwargs)
            
            try:
                result = func(*args, **kwargs)
                if self.enabled:
                    self.trace_call(f"{func.__name__}_result", (), {}, result)
                return result
            except Exception as e:
                if self.enabled:
                    self.trace_call(f"{func.__name__}_error", (), {}, str(e))
                raise
        
        return wrapper
    
    def dump_trace(self, output_file: Optional[str] = None) -> str:
        """
        Dump trace data to string or file.
        
        Args:
            output_file: Optional file path to save trace
            
        Returns:
            Trace data as formatted string
        """
        if not self.trace_data:
            return "No trace data available"
        
        lines = []
        lines.append("=" * 80)
        lines.append("TungShing Debug Trace")
        lines.append("=" * 80)
        lines.append(f"Total calls: {len(self.trace_data)}")
        lines.append("")
        
        for i, trace in enumerate(self.trace_data):
            lines.append(f"[{i:03d}] {trace['function']}")
            lines.append(f"      Time: {trace['timestamp']:.6f}")
            lines.append(f"      Depth: {trace['stack_depth']}")
            if trace['args'] != '()':
                lines.append(f"      Args: {trace['args']}")
            if trace['kwargs'] != '{}':
                lines.append(f"      Kwargs: {trace['kwargs']}")
            if trace['result']:
                lines.append(f"      Result: {trace['result']}")
            lines.append("")
        
        trace_text = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(trace_text)
        
        return trace_text


# Global instances for easy access
_global_profiler = PerformanceProfiler()
_global_tracer = DebugTracer()


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance."""
    return _global_profiler


def get_tracer() -> DebugTracer:
    """Get the global tracer instance."""
    return _global_tracer


def profile_tungshing_creation(iterations: int = 100, dates: Optional[List[datetime]] = None) -> Dict[str, Any]:
    """
    Convenience function to profile TungShing object creation.
    
    Args:
        iterations: Number of iterations per date
        dates: List of dates to test
        
    Returns:
        Profiling results
    """
    if dates is None:
        dates = [datetime.now()]
    
    profiler = PerformanceProfiler()
    return profiler.benchmark_tungshing_operations(dates)


def trace_calculation(func: Callable) -> Callable:
    """
    Decorator to trace TungShing calculations.
    
    Usage:
        @trace_calculation
        def my_calculation():
            ts = TungShing(datetime.now())
            return ts.year8Char
    """
    return _global_tracer.trace_decorator(func)


def memory_benchmark(duration: float = 5.0) -> Dict[str, Any]:
    """
    Convenience function for memory usage analysis.
    
    Args:
        duration: Duration in seconds to monitor
        
    Returns:
        Memory usage analysis
    """
    profiler = PerformanceProfiler()
    return profiler.memory_usage_analysis(duration)