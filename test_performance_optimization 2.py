#!/usr/bin/env python3
"""
Test Performance Optimization System

This script tests the performance optimization components for StosOS
including memory monitoring, resource cleanup, graphics optimization,
and profiling capabilities.
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
from core.graphics_optimizer import GraphicsOptimizer
from core.resource_monitor import ResourceMonitor


class MockWidget:
    """Mock widget for testing animations"""
    def __init__(self):
        self.size = (100, 100)
        self.pos = (0, 0)
        self.opacity = 1.0


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
    print(f"Profiling analysis: {analysis}")
    
    return True


def test_graphics_optimizer():
    """Test the graphics optimizer functionality"""
    print("\n=== Testing Graphics Optimizer ===")
    
    logger = Logger()
    graphics_opt = GraphicsOptimizer(logger)
    
    # Initialize
    graphics_opt.initialize()
    
    # Test frame rate management
    print("Testing frame rate management...")
    for i in range(10):
        frame_time = graphics_opt.frame_manager.start_frame()
        time.sleep(0.016)  # Simulate 60fps
    
    current_fps = graphics_opt.frame_manager.get_current_fps()
    print(f"Current FPS: {current_fps:.1f}")
    print(f"Quality Level: {graphics_opt.frame_manager.get_quality_level():.1f}")
    
    # Test animation optimization
    print("\nTesting animation optimization...")
    mock_widget = MockWidget()
    
    # Create optimized animations
    fade_anim = graphics_opt.animation_optimizer.create_fade_animation(
        mock_widget, 0.5, duration=0.3
    )
    slide_anim = graphics_opt.animation_optimizer.create_slide_animation(
        mock_widget, (100, 100), duration=0.5
    )
    
    print(f"Created fade animation: {fade_anim}")
    print(f"Created slide animation: {slide_anim}")
    
    # Test texture management
    print("\nTesting texture management...")
    def mock_texture_loader():
        return f"texture_data_{time.time()}"
    
    texture1 = graphics_opt.texture_manager.get_cached_texture("test_texture", mock_texture_loader)
    texture2 = graphics_opt.texture_manager.get_cached_texture("test_texture", mock_texture_loader)
    
    print(f"Texture 1: {texture1}")
    print(f"Texture 2: {texture2}")
    print(f"Cache hit (same texture): {texture1 == texture2}")
    
    cache_stats = graphics_opt.texture_manager.get_cache_stats()
    print(f"Cache stats: {cache_stats}")
    
    # Get performance stats
    perf_stats = graphics_opt.get_performance_stats()
    print(f"Graphics performance stats: {perf_stats}")
    
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
    
    # Test system optimization
    print("\nTesting system optimization...")
    opt_result = resource_monitor.optimize_system()
    print(f"Optimization result: {opt_result}")
    
    # Generate system report
    print("\nGenerating system report...")
    report = resource_monitor.get_system_report()
    print(f"System report generated with {len(report)} sections")
    
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
    print("Starting monitoring for 10 seconds...")
    perf_manager.start_monitoring(interval=2.0)
    resource_monitor.start_monitoring(interval=2.0)
    
    # Let it run for a bit
    time.sleep(10)
    
    # Stop monitoring
    perf_manager.stop_monitoring()
    resource_monitor.stop_monitoring()
    
    print(f"Received {len(performance_updates)} performance updates")
    print(f"Received {len(resource_updates)} resource updates")
    print(f"Received {len(alerts)} alerts")
    
    return True


def test_lazy_loading():
    """Test lazy loading functionality"""
    print("\n=== Testing Lazy Loading ===")
    
    logger = Logger()
    perf_manager = PerformanceManager(logger)
    
    # Register lazy modules
    def load_heavy_module():
        print("Loading heavy module...")
        time.sleep(0.5)  # Simulate loading time
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


def main():
    """Run all performance optimization tests"""
    print("StosOS Performance Optimization Test Suite")
    print("=" * 50)
    
    tests = [
        ("Performance Manager", test_performance_manager),
        ("Graphics Optimizer", test_graphics_optimizer),
        ("Resource Monitor", test_resource_monitor),
        ("Monitoring Integration", test_monitoring_integration),
        ("Lazy Loading", test_lazy_loading)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning {test_name} test...")
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            results[test_name] = "ERROR"
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for test_name, result in results.items():
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All performance optimization tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())