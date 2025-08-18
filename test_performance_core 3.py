#!/usr/bin/env python3
"""
Core Performance Optimization Test

This script tests the core performance optimization components without graphics dependencies.
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add the stosos directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.logger import Logger
from core.performance_manager import PerformanceManager, PerformanceMetrics
from core.resource_monitor import ResourceMonitor


class MockModule:
    """Mock module for testing resource management"""
    def __init__(self, name: str):
        self.name = name
        self.data = [0] * 1000  # Some memory usage
    
    def cleanup(self):
        """Cleanup method for testing"""
        self.data.clear()
        print(f"Cleaned up module: {self.name}")


def test_performance_manager():
    """Test the performance manager functionality"""
    print("\n=== Testing Performance Manager ===")
    
    logger = Logger()
    perf_manager = PerformanceManager(logger)
    
    # Test current metrics
    print("Getting current metrics...")
    metrics = perf_manager.get_current_metrics()
    print(f"CPU: {metrics.cpu_percent:.1f}%")
    print(f"Memory: {metrics.memory_percent:.1f}%")
    print(f"Available Memory: {metrics.memory_available_mb:.1f}MB")
    if metrics.temperature_c:
        print(f"Temperature: {metrics.temperature_c:.1f}°C")
    
    # Test module registration and cleanup
    print("\nTesting module registration...")
    mock_module = MockModule("test_module")
    perf_manager.cleanup_manager.register_module(
        "test_module", mock_module, mock_module.cleanup
    )
    
    # Update module usage
    perf_manager.update_module_usage("test_module", 50.0, 10.0, priority=2)
    
    # Test optimization
    print("\nTesting performance optimization...")
    result = perf_manager.optimize_performance()
    print(f"Optimizations performed: {result['optimizations_performed']}")
    
    # Test profiling
    print("\nTesting profiler...")
    perf_manager.profiler.start_profiling()
    
    # Simulate some work
    for i in range(5):
        metrics = perf_manager.get_current_metrics()
        perf_manager.profiler.record_metrics(metrics)
        perf_manager.profiler.record_frame_time(16.67)  # 60fps
        time.sleep(0.1)
    
    analysis = perf_manager.profiler.stop_profiling()
    print(f"Profiling analysis keys: {list(analysis.keys())}")
    
    # Test performance report
    report = perf_manager.get_performance_report()
    print(f"Performance report generated with keys: {list(report.keys())}")
    
    return True


def test_resource_monitor():
    """Test the resource monitor functionality"""
    print("\n=== Testing Resource Monitor ===")
    
    logger = Logger()
    resource_monitor = ResourceMonitor(logger)
    
    # Test current resources
    print("Getting current resources...")
    resources = resource_monitor.get_current_resources()
    print(f"CPU: {resources.cpu_percent:.1f}% @ {resources.cpu_freq_mhz:.0f}MHz")
    print(f"Memory: {resources.memory_used_mb:.1f}MB / {resources.memory_total_mb:.1f}MB ({resources.memory_percent:.1f}%)")
    print(f"Disk: {resources.disk_used_percent:.1f}% used, {resources.disk_free_gb:.1f}GB free")
    print(f"Processes: {resources.processes_count}")
    print(f"Load Average: {resources.load_average}")
    if resources.temperature_c:
        print(f"Temperature: {resources.temperature_c:.1f}°C")
    
    # Test process monitoring
    print("\nTesting process monitoring...")
    top_processes = resource_monitor.process_monitor.get_top_processes(5)
    print("Top 5 processes by resource usage:")
    for proc in top_processes:
        print(f"  {proc.name} (PID {proc.pid}): CPU {proc.cpu_percent:.1f}%, Memory {proc.memory_mb:.1f}MB")
    
    # Test disk monitoring
    print("\nTesting disk monitoring...")
    disk_usage = resource_monitor.disk_monitor.get_disk_usage()
    for mount, usage in disk_usage.items():
        print(f"  {mount}: {usage['used_gb']:.1f}GB / {usage['total_gb']:.1f}GB ({usage['percent']:.1f}%)")
    
    # Test network monitoring
    print("\nTesting network monitoring...")
    network_stats = resource_monitor.network_monitor.get_network_stats()
    print(f"Network - Sent: {network_stats.get('bytes_sent', 0) / (1024*1024):.1f}MB, "
          f"Received: {network_stats.get('bytes_recv', 0) / (1024*1024):.1f}MB")
    
    # Test alert system
    print("\nTesting alert system...")
    resource_monitor.alert_manager.send_alert(
        'info', 'Test Alert', 'This is a test alert message'
    )
    
    alert_history = resource_monitor.alert_manager.get_alert_history(5)
    print(f"Recent alerts: {len(alert_history)}")
    
    # Generate system report
    print("\nGenerating system report...")
    report = resource_monitor.get_system_report()
    print(f"System report generated with {len(report)} sections")
    
    return True


def test_lazy_loading():
    """Test lazy loading functionality"""
    print("\n=== Testing Lazy Loading ===")
    
    logger = Logger()
    perf_manager = PerformanceManager(logger)
    
    # Register lazy modules
    def load_heavy_module():
        print("Loading heavy module...")
        time.sleep(0.2)  # Simulate loading time
        return MockModule("heavy_module")
    
    def load_light_module():
        print("Loading light module...")
        return MockModule("light_module")
    
    perf_manager.lazy_loader.register_lazy_module("heavy", load_heavy_module)
    perf_manager.lazy_loader.register_lazy_module("light", load_light_module)
    
    # Test lazy loading
    print("Getting light module (should load immediately)...")
    light_module = perf_manager.lazy_loader.get_module("light")
    print(f"Light module loaded: {light_module.name}")
    
    print("Getting heavy module (should show loading message)...")
    heavy_module = perf_manager.lazy_loader.get_module("heavy")
    print(f"Heavy module loaded: {heavy_module.name}")
    
    print("Getting heavy module again (should be cached)...")
    heavy_module2 = perf_manager.lazy_loader.get_module("heavy")
    print(f"Same instance: {heavy_module is heavy_module2}")
    
    # Test unloading
    print("Unloading heavy module...")
    perf_manager.lazy_loader.unload_module("heavy")
    
    return True


def test_cleanup_manager():
    """Test resource cleanup functionality"""
    print("\n=== Testing Cleanup Manager ===")
    
    logger = Logger()
    perf_manager = PerformanceManager(logger)
    
    # Create mock modules with different priorities
    modules = []
    for i in range(3):
        module = MockModule(f"module_{i}")
        modules.append(module)
        
        # Register with cleanup manager
        perf_manager.cleanup_manager.register_module(
            f"module_{i}", module, module.cleanup
        )
        
        # Update usage with different priorities
        priority = i + 1  # 1=high, 2=medium, 3=low
        perf_manager.update_module_usage(f"module_{i}", 25.0, 5.0, priority)
    
    # Test emergency cleanup
    print("Testing emergency cleanup...")
    result = perf_manager.cleanup_manager.emergency_cleanup()
    print(f"Emergency cleanup result: {result}")
    
    return True


def test_profiler():
    """Test performance profiler"""
    print("\n=== Testing Performance Profiler ===")
    
    logger = Logger()
    perf_manager = PerformanceManager(logger)
    
    # Start profiling
    perf_manager.profiler.start_profiling()
    
    # Generate some metrics
    for i in range(10):
        metrics = perf_manager.get_current_metrics()
        perf_manager.profiler.record_metrics(metrics)
        
        # Simulate varying frame times
        frame_time = 16.67 + (i * 2)  # Increasing frame times
        perf_manager.profiler.record_frame_time(frame_time)
        
        time.sleep(0.05)
    
    # Stop profiling and get analysis
    analysis = perf_manager.profiler.stop_profiling()
    
    print(f"Profiling duration: {analysis.get('duration_seconds', 0)} seconds")
    
    if 'cpu_stats' in analysis:
        cpu_stats = analysis['cpu_stats']
        print(f"CPU - Avg: {cpu_stats['avg']:.1f}%, Max: {cpu_stats['max']:.1f}%")
    
    if 'memory_stats' in analysis:
        mem_stats = analysis['memory_stats']
        print(f"Memory - Avg: {mem_stats['avg']:.1f}%, Max: {mem_stats['max']:.1f}%")
    
    if 'frame_stats' in analysis:
        frame_stats = analysis['frame_stats']
        print(f"Frame Rate - Avg: {frame_stats['avg_fps']:.1f} FPS")
        print(f"Dropped Frames: {frame_stats['dropped_frames']}")
    
    if 'bottlenecks' in analysis:
        print(f"Bottlenecks detected: {analysis['bottlenecks']}")
    
    return True


def main():
    """Run core performance optimization tests"""
    print("StosOS Performance Optimization Test Suite (Core Components)")
    print("=" * 60)
    
    tests = [
        ("Performance Manager", test_performance_manager),
        ("Resource Monitor", test_resource_monitor),
        ("Lazy Loading", test_lazy_loading),
        ("Cleanup Manager", test_cleanup_manager),
        ("Performance Profiler", test_profiler)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning {test_name} test...")
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = "ERROR"
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All core performance optimization tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())