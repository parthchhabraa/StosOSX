#!/usr/bin/env python3
"""
Simple Performance Optimization Test

This script tests the core performance optimization components without Kivy dependencies.
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


def test_monitoring_integration():
    """Test integrated monitoring with callbacks"""
    print("\n=== Testing Monitoring Integration ===")
    
    logger = Logger()
    perf_manager = PerformanceManager(logger)
    resource_monitor = ResourceMonitor(logger)
    
    # Setup callbacks
    performance_updates = []
    resource_updates = []
    alerts = []
    
    def on_performance_update(metrics):
        performance_updates.append(metrics)
        print(f"Performance update: CPU {metrics.cpu_percent:.1f}%, Memory {metrics.memory_percent:.1f}%")
    
    def on_resource_update(resources):
        resource_updates.append(resources)
        print(f"Resource update: {resources.timestamp}")
    
    def on_alert(level, title, message):
        alerts.append((level, title, message))
        print(f"Alert [{level}]: {title} - {message}")
    
    perf_manager.add_performance_callback(on_performance_update)
    resource_monitor.add_resource_callback(on_resource_update)
    resource_monitor.alert_manager.add_alert_callback(on_alert)
    
    # Start monitoring
    print("Starting monitoring for 5 seconds...")
    perf_manager.start_monitoring(interval=1.0)
    resource_monitor.start_monitoring(interval=1.0)
    
    # Let it run for a bit
    time.sleep(5)
    
    # Stop monitoring
    perf_manager.stop_monitoring()
    resource_monitor.stop_monitoring()
    
    print(f"Received {len(performance_updates)} performance updates")
    print(f"Received {len(resource_updates)} resource updates")
    print(f"Received {len(alerts)} alerts")
    
    return True


def main():
    """Run core performance optimization tests"""
    print("StosOS Performance Optimization Test Suite (Core Components)")
    print("=" * 60)
    
    tests = [
        ("Performance Manager", test_performance_manager),
        ("Resource Monitor", test_resource_monitor),
        ("Lazy Loading", test_lazy_loading),
        ("Monitoring Integration", test_monitoring_integration)
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