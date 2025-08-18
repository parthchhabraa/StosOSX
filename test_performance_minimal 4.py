#!/usr/bin/env python3
"""
Minimal Performance Optimization Test

This script tests the performance optimization components with minimal dependencies.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add the stosos directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Create a simple logger to avoid Kivy imports
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class SimpleLogger:
    """Simple logger wrapper"""
    def __init__(self):
        self.logger = logging.getLogger('stosos_test')
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)


def test_performance_metrics():
    """Test basic performance metrics collection"""
    print("\n=== Testing Performance Metrics ===")
    
    try:
        import psutil
        
        # Test CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        print(f"CPU Usage: {cpu_percent:.1f}%")
        
        # Test memory metrics
        memory = psutil.virtual_memory()
        print(f"Memory Usage: {memory.percent:.1f}%")
        print(f"Available Memory: {memory.available / (1024*1024):.1f}MB")
        
        # Test disk metrics
        disk = psutil.disk_usage('/')
        print(f"Disk Usage: {(disk.used / disk.total) * 100:.1f}%")
        
        # Test process count
        process_count = len(psutil.pids())
        print(f"Process Count: {process_count}")
        
        return True
        
    except Exception as e:
        print(f"Error testing performance metrics: {e}")
        return False


def test_resource_cleanup():
    """Test basic resource cleanup functionality"""
    print("\n=== Testing Resource Cleanup ===")
    
    try:
        # Create some test data
        test_data = []
        for i in range(1000):
            test_data.append([0] * 100)  # Create some memory usage
        
        print(f"Created test data with {len(test_data)} items")
        
        # Clean up
        test_data.clear()
        
        # Force garbage collection
        import gc
        collected = gc.collect()
        print(f"Garbage collection freed {collected} objects")
        
        return True
        
    except Exception as e:
        print(f"Error testing resource cleanup: {e}")
        return False


def test_lazy_loading_concept():
    """Test lazy loading concept"""
    print("\n=== Testing Lazy Loading Concept ===")
    
    try:
        # Simple lazy loader implementation
        class SimpleLazyLoader:
            def __init__(self):
                self._loaded = {}
                self._loaders = {}
            
            def register(self, name, loader_func):
                self._loaders[name] = loader_func
            
            def get(self, name):
                if name not in self._loaded:
                    if name in self._loaders:
                        print(f"Loading {name}...")
                        self._loaded[name] = self._loaders[name]()
                    else:
                        return None
                return self._loaded[name]
        
        # Test the lazy loader
        loader = SimpleLazyLoader()
        
        def create_heavy_object():
            time.sleep(0.1)  # Simulate loading time
            return {"data": list(range(1000))}
        
        loader.register("heavy_object", create_heavy_object)
        
        # First access should trigger loading
        start_time = time.time()
        obj1 = loader.get("heavy_object")
        load_time = time.time() - start_time
        print(f"First access took {load_time:.3f}s")
        
        # Second access should be instant
        start_time = time.time()
        obj2 = loader.get("heavy_object")
        cache_time = time.time() - start_time
        print(f"Second access took {cache_time:.3f}s")
        
        print(f"Same object: {obj1 is obj2}")
        
        return True
        
    except Exception as e:
        print(f"Error testing lazy loading: {e}")
        return False


def test_memory_monitoring():
    """Test memory monitoring functionality"""
    print("\n=== Testing Memory Monitoring ===")
    
    try:
        import psutil
        
        # Get initial memory
        initial_memory = psutil.virtual_memory()
        print(f"Initial memory usage: {initial_memory.percent:.1f}%")
        
        # Create memory load
        memory_hog = []
        for i in range(100):
            memory_hog.append([0] * 10000)
        
        # Check memory after allocation
        after_memory = psutil.virtual_memory()
        print(f"Memory after allocation: {after_memory.percent:.1f}%")
        
        # Clean up
        memory_hog.clear()
        import gc
        gc.collect()
        
        # Check memory after cleanup
        final_memory = psutil.virtual_memory()
        print(f"Memory after cleanup: {final_memory.percent:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"Error testing memory monitoring: {e}")
        return False


def test_process_monitoring():
    """Test process monitoring functionality"""
    print("\n=== Testing Process Monitoring ===")
    
    try:
        import psutil
        
        # Get top processes by memory usage
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
            try:
                info = proc.info
                if info['memory_percent'] and info['memory_percent'] > 0:
                    processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by memory usage
        processes.sort(key=lambda x: x['memory_percent'], reverse=True)
        
        print("Top 5 processes by memory usage:")
        for proc in processes[:5]:
            print(f"  {proc['name']} (PID {proc['pid']}): "
                  f"Memory {proc['memory_percent']:.1f}%, CPU {proc['cpu_percent']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"Error testing process monitoring: {e}")
        return False


def test_temperature_monitoring():
    """Test temperature monitoring (Raspberry Pi specific)"""
    print("\n=== Testing Temperature Monitoring ===")
    
    try:
        # Try to read CPU temperature (Raspberry Pi)
        temp_file = Path('/sys/class/thermal/thermal_zone0/temp')
        if temp_file.exists():
            temp_str = temp_file.read_text().strip()
            temperature = float(temp_str) / 1000.0
            print(f"CPU Temperature: {temperature:.1f}°C")
            
            if temperature > 70:
                print("WARNING: High temperature detected!")
            
            return True
        else:
            print("Temperature monitoring not available (not on Raspberry Pi)")
            return True
            
    except Exception as e:
        print(f"Error testing temperature monitoring: {e}")
        return False


def main():
    """Run minimal performance optimization tests"""
    print("StosOS Performance Optimization Test Suite (Minimal)")
    print("=" * 55)
    
    tests = [
        ("Performance Metrics", test_performance_metrics),
        ("Resource Cleanup", test_resource_cleanup),
        ("Lazy Loading Concept", test_lazy_loading_concept),
        ("Memory Monitoring", test_memory_monitoring),
        ("Process Monitoring", test_process_monitoring),
        ("Temperature Monitoring", test_temperature_monitoring)
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
    print("\n" + "=" * 55)
    print("TEST RESULTS SUMMARY")
    print("=" * 55)
    
    for test_name, result in results.items():
        status_symbol = "✓" if result == "PASS" else "✗"
        print(f"{status_symbol} {test_name}: {result}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All minimal performance optimization tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())