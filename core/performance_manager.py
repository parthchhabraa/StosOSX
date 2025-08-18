"""
Performance Manager for StosOS - Raspberry Pi 4 Optimization

This module provides comprehensive performance monitoring, memory optimization,
resource cleanup, and profiling capabilities specifically designed for
Raspberry Pi 4 hardware constraints.
"""

import psutil
import gc
import time
import threading
import weakref
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json

# Logger will be passed as parameter to avoid circular imports


@dataclass
class PerformanceMetrics:
    """Container for system performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    gpu_memory_mb: Optional[float] = None
    temperature_c: Optional[float] = None
    active_modules: List[str] = field(default_factory=list)
    frame_rate: Optional[float] = None


@dataclass
class ModuleResourceUsage:
    """Track resource usage per module"""
    module_name: str
    memory_mb: float
    cpu_percent: float
    last_active: datetime
    priority: int = 1  # 1=high, 2=medium, 3=low


class ResourceCleanupManager:
    """Manages cleanup of unused resources and modules"""
    
    def __init__(self, logger):
        self.logger = logger
        self._cleanup_callbacks: Dict[str, List[Callable]] = {}
        self._module_refs: Dict[str, weakref.ref] = {}
        self._cleanup_thresholds = {
            'memory_percent': 75.0,  # Trigger cleanup at 75% memory usage
            'inactive_time': 300,    # Cleanup modules inactive for 5 minutes
            'low_priority_time': 120  # Cleanup low priority modules after 2 minutes
        }
    
    def register_module(self, module_name: str, module_ref: Any, 
                       cleanup_callback: Optional[Callable] = None):
        """Register a module for resource tracking and cleanup"""
        self._module_refs[module_name] = weakref.ref(module_ref)
        
        if cleanup_callback:
            if module_name not in self._cleanup_callbacks:
                self._cleanup_callbacks[module_name] = []
            self._cleanup_callbacks[module_name].append(cleanup_callback)
    
    def add_cleanup_callback(self, module_name: str, callback: Callable):
        """Add a cleanup callback for a module"""
        if module_name not in self._cleanup_callbacks:
            self._cleanup_callbacks[module_name] = []
        self._cleanup_callbacks[module_name].append(callback)
    
    def cleanup_module(self, module_name: str) -> bool:
        """Clean up resources for a specific module"""
        try:
            # Execute cleanup callbacks
            if module_name in self._cleanup_callbacks:
                for callback in self._cleanup_callbacks[module_name]:
                    try:
                        callback()
                    except Exception as e:
                        self.logger.error(f"Cleanup callback failed for {module_name}: {e}")
            
            # Remove weak reference
            if module_name in self._module_refs:
                del self._module_refs[module_name]
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info(f"Cleaned up resources for module: {module_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup module {module_name}: {e}")
            return False
    
    def cleanup_inactive_modules(self, module_usage: Dict[str, ModuleResourceUsage]) -> List[str]:
        """Clean up modules that have been inactive for too long"""
        cleaned_modules = []
        current_time = datetime.now()
        
        for module_name, usage in module_usage.items():
            inactive_time = (current_time - usage.last_active).total_seconds()
            
            # Determine cleanup threshold based on priority
            if usage.priority == 3:  # Low priority
                threshold = self._cleanup_thresholds['low_priority_time']
            else:
                threshold = self._cleanup_thresholds['inactive_time']
            
            if inactive_time > threshold:
                if self.cleanup_module(module_name):
                    cleaned_modules.append(module_name)
        
        return cleaned_modules
    
    def emergency_cleanup(self) -> bool:
        """Perform emergency cleanup when memory is critically low"""
        try:
            self.logger.warning("Performing emergency resource cleanup")
            
            # Force garbage collection
            gc.collect()
            
            # Clean up all low priority modules
            for module_name in list(self._module_refs.keys()):
                self.cleanup_module(module_name)
            
            # Additional cleanup measures
            self._clear_caches()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Emergency cleanup failed: {e}")
            return False
    
    def _clear_caches(self):
        """Clear various system caches"""
        # Clear Python's internal caches
        gc.collect()
        
        # Clear any application-specific caches here
        # This would be extended based on specific cache implementations


class LazyLoader:
    """Implements lazy loading for heavy modules and resources"""
    
    def __init__(self, logger):
        self.logger = logger
        self._loaded_modules: Dict[str, Any] = {}
        self._module_loaders: Dict[str, Callable] = {}
        self._loading_locks: Dict[str, threading.Lock] = {}
    
    def register_lazy_module(self, module_name: str, loader_func: Callable):
        """Register a module for lazy loading"""
        self._module_loaders[module_name] = loader_func
        self._loading_locks[module_name] = threading.Lock()
    
    def get_module(self, module_name: str) -> Optional[Any]:
        """Get a module, loading it lazily if needed"""
        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]
        
        if module_name not in self._module_loaders:
            self.logger.error(f"No loader registered for module: {module_name}")
            return None
        
        with self._loading_locks[module_name]:
            # Double-check pattern
            if module_name in self._loaded_modules:
                return self._loaded_modules[module_name]
            
            try:
                self.logger.info(f"Lazy loading module: {module_name}")
                start_time = time.time()
                
                module = self._module_loaders[module_name]()
                self._loaded_modules[module_name] = module
                
                load_time = time.time() - start_time
                self.logger.info(f"Module {module_name} loaded in {load_time:.2f}s")
                
                return module
                
            except Exception as e:
                self.logger.error(f"Failed to load module {module_name}: {e}")
                return None
    
    def unload_module(self, module_name: str) -> bool:
        """Unload a module to free memory"""
        if module_name in self._loaded_modules:
            try:
                del self._loaded_modules[module_name]
                gc.collect()
                self.logger.info(f"Unloaded module: {module_name}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to unload module {module_name}: {e}")
                return False
        return True


class PerformanceProfiler:
    """Profiles system performance and identifies bottlenecks"""
    
    def __init__(self, logger):
        self.logger = logger
        self._profiling_active = False
        self._profile_data: List[PerformanceMetrics] = []
        self._frame_times: List[float] = []
        self._max_profile_entries = 1000
    
    def start_profiling(self):
        """Start performance profiling"""
        self._profiling_active = True
        self._profile_data.clear()
        self._frame_times.clear()
        self.logger.info("Performance profiling started")
    
    def stop_profiling(self) -> Dict[str, Any]:
        """Stop profiling and return analysis"""
        self._profiling_active = False
        analysis = self._analyze_profile_data()
        self.logger.info("Performance profiling stopped")
        return analysis
    
    def record_frame_time(self, frame_time: float):
        """Record frame rendering time"""
        if self._profiling_active:
            self._frame_times.append(frame_time)
            if len(self._frame_times) > self._max_profile_entries:
                self._frame_times.pop(0)
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics"""
        if self._profiling_active:
            self._profile_data.append(metrics)
            if len(self._profile_data) > self._max_profile_entries:
                self._profile_data.pop(0)
    
    def _analyze_profile_data(self) -> Dict[str, Any]:
        """Analyze collected profile data"""
        if not self._profile_data:
            return {}
        
        # Calculate statistics
        cpu_values = [m.cpu_percent for m in self._profile_data]
        memory_values = [m.memory_percent for m in self._profile_data]
        
        analysis = {
            'duration_seconds': len(self._profile_data),
            'cpu_stats': {
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory_stats': {
                'avg': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'bottlenecks': self._identify_bottlenecks()
        }
        
        if self._frame_times:
            analysis['frame_stats'] = {
                'avg_fps': 1000.0 / (sum(self._frame_times) / len(self._frame_times)),
                'avg_frame_time_ms': sum(self._frame_times) / len(self._frame_times),
                'max_frame_time_ms': max(self._frame_times),
                'dropped_frames': len([t for t in self._frame_times if t > 33.33])  # >30fps
            }
        
        return analysis
    
    def _identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks"""
        bottlenecks = []
        
        if not self._profile_data:
            return bottlenecks
        
        # Check for high CPU usage
        high_cpu_count = len([m for m in self._profile_data if m.cpu_percent > 80])
        if high_cpu_count > len(self._profile_data) * 0.1:  # >10% of time
            bottlenecks.append("High CPU usage detected")
        
        # Check for high memory usage
        high_memory_count = len([m for m in self._profile_data if m.memory_percent > 75])
        if high_memory_count > len(self._profile_data) * 0.1:
            bottlenecks.append("High memory usage detected")
        
        # Check for poor frame rates
        if self._frame_times:
            slow_frames = len([t for t in self._frame_times if t > 33.33])
            if slow_frames > len(self._frame_times) * 0.1:
                bottlenecks.append("Poor frame rate performance")
        
        return bottlenecks


class PerformanceManager:
    """Main performance management system for StosOS"""
    
    def __init__(self, logger):
        self.logger = logger
        self.cleanup_manager = ResourceCleanupManager(logger)
        self.lazy_loader = LazyLoader(logger)
        self.profiler = PerformanceProfiler(logger)
        
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        self._module_usage: Dict[str, ModuleResourceUsage] = {}
        
        # Performance thresholds for Raspberry Pi 4
        self._thresholds = {
            'memory_warning': 70.0,    # Warn at 70% memory usage
            'memory_critical': 85.0,   # Critical at 85% memory usage
            'cpu_warning': 80.0,       # Warn at 80% CPU usage
            'temperature_warning': 70.0, # Warn at 70°C
            'temperature_critical': 80.0  # Critical at 80°C
        }
        
        self._performance_callbacks: List[Callable[[PerformanceMetrics], None]] = []
    
    def start_monitoring(self, interval: float = 5.0):
        """Start performance monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self._monitoring_thread.start()
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=1.0)
        self.logger.info("Performance monitoring stopped")
    
    def add_performance_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """Add callback to be called with performance metrics"""
        self._performance_callbacks.append(callback)
    
    def get_current_metrics(self) -> PerformanceMetrics:
        """Get current system performance metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Try to get temperature (Raspberry Pi specific)
            temperature = self._get_cpu_temperature()
            
            # Try to get GPU memory (if available)
            gpu_memory = self._get_gpu_memory()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                gpu_memory_mb=gpu_memory,
                temperature_c=temperature,
                active_modules=list(self._module_usage.keys())
            )
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get performance metrics: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=0.0
            )
    
    def update_module_usage(self, module_name: str, memory_mb: float, 
                          cpu_percent: float, priority: int = 1):
        """Update resource usage for a module"""
        self._module_usage[module_name] = ModuleResourceUsage(
            module_name=module_name,
            memory_mb=memory_mb,
            cpu_percent=cpu_percent,
            last_active=datetime.now(),
            priority=priority
        )
    
    def optimize_performance(self) -> Dict[str, Any]:
        """Perform performance optimization"""
        metrics = self.get_current_metrics()
        optimizations = []
        
        # Check if cleanup is needed
        if metrics.memory_percent > self._thresholds['memory_warning']:
            cleaned = self.cleanup_manager.cleanup_inactive_modules(self._module_usage)
            if cleaned:
                optimizations.append(f"Cleaned up modules: {', '.join(cleaned)}")
        
        # Emergency cleanup if critical
        if metrics.memory_percent > self._thresholds['memory_critical']:
            if self.cleanup_manager.emergency_cleanup():
                optimizations.append("Performed emergency cleanup")
        
        # Force garbage collection
        gc.collect()
        optimizations.append("Performed garbage collection")
        
        return {
            'optimizations_performed': optimizations,
            'metrics_before': metrics,
            'metrics_after': self.get_current_metrics()
        }
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self._monitoring_active:
            try:
                metrics = self.get_current_metrics()
                
                # Record metrics for profiling
                self.profiler.record_metrics(metrics)
                
                # Check thresholds and take action
                self._check_thresholds(metrics)
                
                # Notify callbacks
                for callback in self._performance_callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        self.logger.error(f"Performance callback failed: {e}")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(interval)
    
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check performance thresholds and take action"""
        # Memory warnings
        if metrics.memory_percent > self._thresholds['memory_critical']:
            self.logger.warning(f"Critical memory usage: {metrics.memory_percent:.1f}%")
            self.cleanup_manager.emergency_cleanup()
        elif metrics.memory_percent > self._thresholds['memory_warning']:
            self.logger.warning(f"High memory usage: {metrics.memory_percent:.1f}%")
            self.cleanup_manager.cleanup_inactive_modules(self._module_usage)
        
        # CPU warnings
        if metrics.cpu_percent > self._thresholds['cpu_warning']:
            self.logger.warning(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        # Temperature warnings
        if metrics.temperature_c:
            if metrics.temperature_c > self._thresholds['temperature_critical']:
                self.logger.error(f"Critical temperature: {metrics.temperature_c:.1f}°C")
            elif metrics.temperature_c > self._thresholds['temperature_warning']:
                self.logger.warning(f"High temperature: {metrics.temperature_c:.1f}°C")
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature (Raspberry Pi specific)"""
        try:
            temp_file = Path('/sys/class/thermal/thermal_zone0/temp')
            if temp_file.exists():
                temp_str = temp_file.read_text().strip()
                return float(temp_str) / 1000.0  # Convert from millidegrees
        except Exception:
            pass
        return None
    
    def _get_gpu_memory(self) -> Optional[float]:
        """Get GPU memory usage (if available)"""
        try:
            # This would need to be implemented based on available GPU monitoring tools
            # For Raspberry Pi, this might use vcgencmd
            import subprocess
            result = subprocess.run(['vcgencmd', 'get_mem', 'gpu'], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                # Parse output like "gpu=64M"
                gpu_mem_str = result.stdout.strip().split('=')[1].rstrip('M')
                return float(gpu_mem_str)
        except Exception:
            pass
        return None
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        current_metrics = self.get_current_metrics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'current_metrics': {
                'cpu_percent': current_metrics.cpu_percent,
                'memory_percent': current_metrics.memory_percent,
                'memory_available_mb': current_metrics.memory_available_mb,
                'temperature_c': current_metrics.temperature_c,
                'active_modules': current_metrics.active_modules
            },
            'module_usage': {
                name: {
                    'memory_mb': usage.memory_mb,
                    'cpu_percent': usage.cpu_percent,
                    'last_active': usage.last_active.isoformat(),
                    'priority': usage.priority
                }
                for name, usage in self._module_usage.items()
            },
            'thresholds': self._thresholds,
            'recommendations': self._generate_recommendations(current_metrics)
        }
        
        return report
    
    def _generate_recommendations(self, metrics: PerformanceMetrics) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        if metrics.memory_percent > 60:
            recommendations.append("Consider closing unused modules to free memory")
        
        if metrics.cpu_percent > 70:
            recommendations.append("High CPU usage detected - check for background processes")
        
        if metrics.temperature_c and metrics.temperature_c > 65:
            recommendations.append("Consider improving cooling or reducing system load")
        
        if len(self._module_usage) > 5:
            recommendations.append("Many modules active - consider lazy loading")
        
        return recommendations