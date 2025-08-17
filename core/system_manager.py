"""
System Manager for StosOS
Handles system lifecycle, shutdown, restart, and health monitoring with performance optimization
"""

import os
import sys
import signal
import subprocess
import threading
import time
import psutil
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import logging
from .config_manager import ConfigManager
from .performance_manager import PerformanceManager
from .graphics_optimizer import GraphicsOptimizer
from .resource_monitor import ResourceMonitor


class SystemManager:
    """Manages system lifecycle and health monitoring"""
    
    def __init__(self, config_manager: ConfigManager, logger: logging.Logger):
        self.config = config_manager
        self.logger = logger
        self.shutdown_callbacks = []
        self.health_monitors = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.restart_requested = False
        
        # Initialize performance optimization components
        from .logger import stosos_logger
        self.performance_manager = PerformanceManager(stosos_logger)
        self.graphics_optimizer = GraphicsOptimizer(stosos_logger)
        self.resource_monitor = ResourceMonitor(stosos_logger)
        
        # System health thresholds
        self.memory_threshold = 0.85  # 85% memory usage
        self.cpu_threshold = 0.90     # 90% CPU usage
        self.temp_threshold = 80.0    # 80°C temperature
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
        
        # Setup performance optimization
        self._setup_performance_optimization()
        
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown")
        self.shutdown()
        
    def register_shutdown_callback(self, callback: Callable):
        """Register a callback to be called during shutdown"""
        self.shutdown_callbacks.append(callback)
        
    def _setup_performance_optimization(self):
        """Setup performance optimization for the system"""
        try:
            # Initialize graphics optimization
            self.graphics_optimizer.initialize()
            
            # Check if running on Raspberry Pi and apply optimizations
            if self._is_raspberry_pi():
                self.graphics_optimizer.optimize_for_raspberry_pi()
                self.logger.info("Applied Raspberry Pi optimizations")
            
            # Setup performance monitoring callbacks
            self.performance_manager.add_performance_callback(self._on_performance_update)
            self.resource_monitor.add_resource_callback(self._on_resource_update)
            
            # Setup alert callbacks
            self.resource_monitor.alert_manager.add_alert_callback(self._on_system_alert)
            
            self.logger.info("Performance optimization setup complete")
            
        except Exception as e:
            self.logger.error(f"Failed to setup performance optimization: {e}")
    
    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def _on_performance_update(self, metrics):
        """Handle performance metrics updates"""
        # Log critical performance issues
        if metrics.memory_percent > 90:
            self.logger.warning(f"Critical memory usage: {metrics.memory_percent:.1f}%")
        if metrics.cpu_percent > 95:
            self.logger.warning(f"Critical CPU usage: {metrics.cpu_percent:.1f}%")
    
    def _on_resource_update(self, resources):
        """Handle resource updates"""
        # Trigger optimization if resources are constrained
        if resources.memory_percent > 85 or resources.cpu_percent > 90:
            self.performance_manager.optimize_performance()
    
    def _on_system_alert(self, level: str, title: str, message: str):
        """Handle system alerts"""
        if level == 'critical':
            self.logger.error(f"SYSTEM ALERT: {title} - {message}")
            # Trigger emergency optimization
            self.performance_manager.optimize_performance()
        else:
            self.logger.warning(f"SYSTEM ALERT: {title} - {message}")

    def start_health_monitoring(self):
        """Start system health monitoring in background thread"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._health_monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        # Start performance monitoring
        self.performance_manager.start_monitoring()
        self.resource_monitor.start_monitoring()
        
        self.logger.info("System health monitoring started")
        
    def stop_health_monitoring(self):
        """Stop system health monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        # Stop performance monitoring
        self.performance_manager.stop_monitoring()
        self.resource_monitor.stop_monitoring()
        
        self.logger.info("System health monitoring stopped")
        
    def _health_monitoring_loop(self):
        """Main health monitoring loop"""
        while self.monitoring_active:
            try:
                health_status = self.get_system_health()
                
                # Check for critical issues
                if health_status['memory_usage'] > self.memory_threshold:
                    self.logger.warning(f"High memory usage: {health_status['memory_usage']:.1%}")
                    self._handle_high_memory()
                    
                if health_status['cpu_usage'] > self.cpu_threshold:
                    self.logger.warning(f"High CPU usage: {health_status['cpu_usage']:.1%}")
                    
                if health_status['temperature'] > self.temp_threshold:
                    self.logger.warning(f"High temperature: {health_status['temperature']:.1f}°C")
                    self._handle_high_temperature()
                    
                # Log health status periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self.logger.info(f"System health: {health_status}")
                    
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                
            time.sleep(30)  # Check every 30 seconds
            
    def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            
            # CPU usage (average over 1 second)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Temperature (Raspberry Pi specific)
            temperature = self._get_cpu_temperature()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network status
            network_active = self._check_network_connectivity()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'memory_usage': memory.percent / 100.0,
                'memory_available_mb': memory.available // (1024 * 1024),
                'cpu_usage': cpu_percent / 100.0,
                'temperature': temperature,
                'disk_usage': disk.percent / 100.0,
                'disk_free_gb': disk.free // (1024 * 1024 * 1024),
                'network_active': network_active,
                'uptime_seconds': time.time() - psutil.boot_time()
            }
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {}
            
    def _get_cpu_temperature(self) -> float:
        """Get CPU temperature on Raspberry Pi"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
                return temp
        except:
            return 0.0
            
    def _check_network_connectivity(self) -> bool:
        """Check if network is available"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', '8.8.8.8'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
            
    def _handle_high_memory(self):
        """Handle high memory usage"""
        try:
            # Force garbage collection
            import gc
            gc.collect()
            
            # Log memory usage by process
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
                    
            # Sort by memory usage
            processes.sort(key=lambda x: x['memory_percent'], reverse=True)
            
            self.logger.info("Top memory consumers:")
            for proc in processes[:5]:
                self.logger.info(f"  {proc['name']} (PID {proc['pid']}): {proc['memory_percent']:.1f}%")
                
        except Exception as e:
            self.logger.error(f"Error handling high memory: {e}")
            
    def _handle_high_temperature(self):
        """Handle high temperature"""
        try:
            # Reduce CPU frequency if possible
            subprocess.run(['sudo', 'cpufreq-set', '-g', 'powersave'], 
                         capture_output=True, timeout=5)
            self.logger.info("Switched to powersave CPU governor due to high temperature")
        except:
            pass
            
    def restart_system(self):
        """Restart the StosOS application"""
        self.logger.info("Restart requested")
        self.restart_requested = True
        self.shutdown()
        
    def shutdown(self):
        """Perform graceful shutdown"""
        self.logger.info("Starting graceful shutdown")
        
        # Stop health monitoring
        self.stop_health_monitoring()
        
        # Call all registered shutdown callbacks
        for callback in self.shutdown_callbacks:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Error in shutdown callback: {e}")
                
        # Save any pending data
        self._save_system_state()
        
        self.logger.info("Graceful shutdown completed")
        
        # Exit or restart
        if self.restart_requested:
            self.logger.info("Restarting StosOS")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            sys.exit(0)
            
    def _save_system_state(self):
        """Save current system state before shutdown"""
        try:
            state = {
                'shutdown_time': datetime.now().isoformat(),
                'uptime_seconds': time.time() - psutil.boot_time(),
                'clean_shutdown': True
            }
            
            state_file = os.path.join(self.config.get_data_dir(), 'system_state.json')
            import json
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving system state: {e}")
            
    def get_last_shutdown_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the last shutdown"""
        try:
            state_file = os.path.join(self.config.get_data_dir(), 'system_state.json')
            if os.path.exists(state_file):
                import json
                with open(state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error reading last shutdown info: {e}")
        return None
        
    def is_service_running(self) -> bool:
        """Check if StosOS is running as a systemd service"""
        try:
            result = subprocess.run(
                ['systemctl', '--user', 'is-active', 'stosos'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0 and result.stdout.strip() == 'active'
        except:
            return False
            
    def restart_service(self):
        """Restart the systemd service"""
        try:
            subprocess.run(['systemctl', '--user', 'restart', 'stosos'], 
                         check=True)
            self.logger.info("StosOS service restarted")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to restart service: {e}")
            
    def stop_service(self):
        """Stop the systemd service"""
        try:
            subprocess.run(['systemctl', '--user', 'stop', 'stosos'], 
                         check=True)
            self.logger.info("StosOS service stopped")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to stop service: {e}")
    
    def optimize_system_performance(self) -> Dict[str, Any]:
        """Perform comprehensive system performance optimization"""
        try:
            results = {}
            
            # Performance manager optimization
            perf_result = self.performance_manager.optimize_performance()
            results['performance_optimization'] = perf_result
            
            # Resource monitor optimization
            resource_result = self.resource_monitor.optimize_system()
            results['resource_optimization'] = resource_result
            
            # Graphics optimization cleanup
            self.graphics_optimizer.cleanup()
            results['graphics_cleanup'] = True
            
            self.logger.info("System performance optimization completed")
            return results
            
        except Exception as e:
            self.logger.error(f"System optimization failed: {e}")
            return {'error': str(e)}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'system_health': self.get_system_health(),
                'performance_metrics': self.performance_manager.get_performance_report(),
                'resource_status': self.resource_monitor.get_system_report(),
                'graphics_stats': self.graphics_optimizer.get_performance_stats()
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            return {'error': str(e)}
    
    def register_module_for_optimization(self, module_name: str, module_ref: Any, 
                                       cleanup_callback: Optional[Callable] = None):
        """Register a module for performance optimization"""
        try:
            self.performance_manager.cleanup_manager.register_module(
                module_name, module_ref, cleanup_callback
            )
            self.logger.info(f"Registered module for optimization: {module_name}")
        except Exception as e:
            self.logger.error(f"Failed to register module {module_name}: {e}")
    
    def create_optimized_animation(self, widget, **kwargs):
        """Create performance-optimized animation"""
        return self.graphics_optimizer.create_optimized_animation(widget, **kwargs)
    
    def update_module_usage(self, module_name: str, memory_mb: float, 
                          cpu_percent: float, priority: int = 1):
        """Update resource usage for a module"""
        self.performance_manager.update_module_usage(
            module_name, memory_mb, cpu_percent, priority
        )