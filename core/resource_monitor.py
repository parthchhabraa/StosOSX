"""
Resource Monitor for StosOS - System Resource Tracking and Optimization

This module provides comprehensive system resource monitoring, alerting,
and automatic optimization for Raspberry Pi 4 hardware.
"""

import psutil
import time
import threading
import json
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import subprocess

from .logger import Logger
from .performance_manager import PerformanceMetrics


@dataclass
class SystemResources:
    """System resource snapshot"""
    timestamp: datetime
    cpu_percent: float
    cpu_freq_mhz: float
    memory_total_mb: float
    memory_used_mb: float
    memory_percent: float
    disk_used_percent: float
    disk_free_gb: float
    temperature_c: Optional[float]
    gpu_memory_mb: Optional[float]
    network_bytes_sent: int
    network_bytes_recv: int
    processes_count: int
    load_average: List[float]


@dataclass
class ProcessInfo:
    """Process information"""
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    status: str
    create_time: datetime


class AlertManager:
    """Manages system alerts and notifications"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self._alert_callbacks: List[Callable[[str, str, str], None]] = []
        self._alert_history: List[Dict[str, Any]] = []
        self._alert_cooldowns: Dict[str, datetime] = {}
        self._cooldown_duration = timedelta(minutes=5)
    
    def add_alert_callback(self, callback: Callable[[str, str, str], None]):
        """Add callback for alerts (level, title, message)"""
        self._alert_callbacks.append(callback)
    
    def send_alert(self, level: str, title: str, message: str, 
                   alert_type: str = "system"):
        """Send system alert"""
        # Check cooldown
        cooldown_key = f"{alert_type}_{title}"
        now = datetime.now()
        
        if cooldown_key in self._alert_cooldowns:
            if now - self._alert_cooldowns[cooldown_key] < self._cooldown_duration:
                return  # Skip duplicate alert
        
        self._alert_cooldowns[cooldown_key] = now
        
        # Log alert
        alert_data = {
            'timestamp': now.isoformat(),
            'level': level,
            'title': title,
            'message': message,
            'type': alert_type
        }
        
        self._alert_history.append(alert_data)
        
        # Keep only last 100 alerts
        if len(self._alert_history) > 100:
            self._alert_history.pop(0)
        
        # Log based on level
        if level == 'critical':
            self.logger.error(f"ALERT: {title} - {message}")
        elif level == 'warning':
            self.logger.warning(f"ALERT: {title} - {message}")
        else:
            self.logger.info(f"ALERT: {title} - {message}")
        
        # Notify callbacks
        for callback in self._alert_callbacks:
            try:
                callback(level, title, message)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")
    
    def get_alert_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return self._alert_history[-limit:]


class ProcessMonitor:
    """Monitors system processes"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self._process_cache: Dict[int, ProcessInfo] = {}
        self._high_cpu_threshold = 20.0  # %
        self._high_memory_threshold = 100.0  # MB
    
    def get_top_processes(self, limit: int = 10) -> List[ProcessInfo]:
        """Get top processes by CPU and memory usage"""
        processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'create_time']):
                try:
                    info = proc.info
                    if info['memory_info']:
                        memory_mb = info['memory_info'].rss / (1024 * 1024)
                        
                        process_info = ProcessInfo(
                            pid=info['pid'],
                            name=info['name'] or 'Unknown',
                            cpu_percent=info['cpu_percent'] or 0.0,
                            memory_mb=memory_mb,
                            status=info['status'],
                            create_time=datetime.fromtimestamp(info['create_time'])
                        )
                        
                        processes.append(process_info)
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage, then memory
            processes.sort(key=lambda p: (p.cpu_percent, p.memory_mb), reverse=True)
            return processes[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get process list: {e}")
            return []
    
    def find_resource_hogs(self) -> List[ProcessInfo]:
        """Find processes using excessive resources"""
        hogs = []
        
        for process in self.get_top_processes(20):
            if (process.cpu_percent > self._high_cpu_threshold or 
                process.memory_mb > self._high_memory_threshold):
                hogs.append(process)
        
        return hogs
    
    def kill_process(self, pid: int, force: bool = False) -> bool:
        """Kill a process by PID"""
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            
            self.logger.info(f"{'Killed' if force else 'Terminated'} process {pid}")
            return True
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.logger.error(f"Failed to kill process {pid}: {e}")
            return False


class DiskMonitor:
    """Monitors disk usage and cleanup"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self._cleanup_paths = [
            '/tmp',
            '/var/log',
            '~/.cache',
            '/var/cache'
        ]
    
    def get_disk_usage(self) -> Dict[str, Dict[str, float]]:
        """Get disk usage for all mounted filesystems"""
        usage = {}
        
        try:
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    usage[partition.mountpoint] = {
                        'total_gb': partition_usage.total / (1024**3),
                        'used_gb': partition_usage.used / (1024**3),
                        'free_gb': partition_usage.free / (1024**3),
                        'percent': (partition_usage.used / partition_usage.total) * 100
                    }
                except PermissionError:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to get disk usage: {e}")
        
        return usage
    
    def cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary files"""
        cleaned = {
            'files_removed': 0,
            'space_freed_mb': 0,
            'errors': []
        }
        
        for path_str in self._cleanup_paths:
            try:
                path = Path(path_str).expanduser()
                if not path.exists():
                    continue
                
                # Clean files older than 7 days
                cutoff_time = time.time() - (7 * 24 * 3600)
                
                for file_path in path.rglob('*'):
                    try:
                        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                            size_mb = file_path.stat().st_size / (1024 * 1024)
                            file_path.unlink()
                            cleaned['files_removed'] += 1
                            cleaned['space_freed_mb'] += size_mb
                    except Exception as e:
                        cleaned['errors'].append(f"Failed to remove {file_path}: {e}")
                        
            except Exception as e:
                cleaned['errors'].append(f"Failed to clean {path_str}: {e}")
        
        self.logger.info(f"Cleanup: {cleaned['files_removed']} files, "
                        f"{cleaned['space_freed_mb']:.1f}MB freed")
        
        return cleaned


class NetworkMonitor:
    """Monitors network usage"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self._last_stats = None
        self._last_time = None
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        try:
            stats = psutil.net_io_counters()
            current_time = time.time()
            
            result = {
                'bytes_sent': stats.bytes_sent,
                'bytes_recv': stats.bytes_recv,
                'packets_sent': stats.packets_sent,
                'packets_recv': stats.packets_recv,
                'errors_in': stats.errin,
                'errors_out': stats.errout,
                'drops_in': stats.dropin,
                'drops_out': stats.dropout
            }
            
            # Calculate rates if we have previous data
            if self._last_stats and self._last_time:
                time_diff = current_time - self._last_time
                if time_diff > 0:
                    result['send_rate_mbps'] = (
                        (stats.bytes_sent - self._last_stats.bytes_sent) / time_diff
                    ) / (1024 * 1024)
                    result['recv_rate_mbps'] = (
                        (stats.bytes_recv - self._last_stats.bytes_recv) / time_diff
                    ) / (1024 * 1024)
            
            self._last_stats = stats
            self._last_time = current_time
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get network stats: {e}")
            return {}


class ResourceMonitor:
    """Main resource monitoring system"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.alert_manager = AlertManager(logger)
        self.process_monitor = ProcessMonitor(logger)
        self.disk_monitor = DiskMonitor(logger)
        self.network_monitor = NetworkMonitor(logger)
        
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        self._resource_history: List[SystemResources] = []
        self._max_history = 720  # 1 hour at 5-second intervals
        
        # Thresholds for alerts
        self._thresholds = {
            'cpu_critical': 90.0,
            'cpu_warning': 75.0,
            'memory_critical': 90.0,
            'memory_warning': 80.0,
            'disk_critical': 95.0,
            'disk_warning': 85.0,
            'temperature_critical': 80.0,
            'temperature_warning': 70.0,
            'load_critical': 4.0,  # For 4-core Pi
            'load_warning': 3.0
        }
        
        self._resource_callbacks: List[Callable[[SystemResources], None]] = []
    
    def start_monitoring(self, interval: float = 5.0):
        """Start resource monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self._monitoring_thread.start()
        self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=2.0)
        self.logger.info("Resource monitoring stopped")
    
    def add_resource_callback(self, callback: Callable[[SystemResources], None]):
        """Add callback for resource updates"""
        self._resource_callbacks.append(callback)
    
    def get_current_resources(self) -> SystemResources:
        """Get current system resource snapshot"""
        try:
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_freq_mhz = cpu_freq.current if cpu_freq else 0.0
            
            # Memory info
            memory = psutil.virtual_memory()
            
            # Disk info
            disk = psutil.disk_usage('/')
            
            # Load average
            load_avg = list(psutil.getloadavg())
            
            # Network info
            net_stats = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Temperature (Raspberry Pi specific)
            temperature = self._get_cpu_temperature()
            
            # GPU memory (if available)
            gpu_memory = self._get_gpu_memory()
            
            return SystemResources(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                cpu_freq_mhz=cpu_freq_mhz,
                memory_total_mb=memory.total / (1024 * 1024),
                memory_used_mb=memory.used / (1024 * 1024),
                memory_percent=memory.percent,
                disk_used_percent=(disk.used / disk.total) * 100,
                disk_free_gb=disk.free / (1024**3),
                temperature_c=temperature,
                gpu_memory_mb=gpu_memory,
                network_bytes_sent=net_stats.bytes_sent,
                network_bytes_recv=net_stats.bytes_recv,
                processes_count=process_count,
                load_average=load_avg
            )
            
        except Exception as e:
            self.logger.error(f"Failed to get system resources: {e}")
            return SystemResources(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                cpu_freq_mhz=0.0,
                memory_total_mb=0.0,
                memory_used_mb=0.0,
                memory_percent=0.0,
                disk_used_percent=0.0,
                disk_free_gb=0.0,
                temperature_c=None,
                gpu_memory_mb=None,
                network_bytes_sent=0,
                network_bytes_recv=0,
                processes_count=0,
                load_average=[0.0, 0.0, 0.0]
            )
    
    def get_resource_history(self, hours: int = 1) -> List[SystemResources]:
        """Get resource history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [r for r in self._resource_history if r.timestamp >= cutoff_time]
    
    def optimize_system(self) -> Dict[str, Any]:
        """Perform system optimization"""
        optimizations = []
        
        try:
            # Clean up disk space
            cleanup_result = self.disk_monitor.cleanup_temp_files()
            if cleanup_result['files_removed'] > 0:
                optimizations.append(f"Cleaned {cleanup_result['files_removed']} temp files")
            
            # Kill resource hogs if memory is critical
            resources = self.get_current_resources()
            if resources.memory_percent > self._thresholds['memory_critical']:
                hogs = self.process_monitor.find_resource_hogs()
                for hog in hogs[:3]:  # Kill top 3 resource hogs
                    if 'stosos' not in hog.name.lower():  # Don't kill ourselves
                        if self.process_monitor.kill_process(hog.pid):
                            optimizations.append(f"Killed process {hog.name} (PID: {hog.pid})")
            
            # Force garbage collection
            import gc
            gc.collect()
            optimizations.append("Performed garbage collection")
            
            return {
                'optimizations': optimizations,
                'cleanup_result': cleanup_result,
                'resources_after': self.get_current_resources()
            }
            
        except Exception as e:
            self.logger.error(f"System optimization failed: {e}")
            return {'optimizations': [], 'error': str(e)}
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self._monitoring_active:
            try:
                resources = self.get_current_resources()
                
                # Add to history
                self._resource_history.append(resources)
                if len(self._resource_history) > self._max_history:
                    self._resource_history.pop(0)
                
                # Check thresholds and send alerts
                self._check_thresholds(resources)
                
                # Notify callbacks
                for callback in self._resource_callbacks:
                    try:
                        callback(resources)
                    except Exception as e:
                        self.logger.error(f"Resource callback failed: {e}")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(interval)
    
    def _check_thresholds(self, resources: SystemResources):
        """Check resource thresholds and send alerts"""
        # CPU alerts
        if resources.cpu_percent > self._thresholds['cpu_critical']:
            self.alert_manager.send_alert(
                'critical', 'High CPU Usage',
                f'CPU usage at {resources.cpu_percent:.1f}%', 'cpu'
            )
        elif resources.cpu_percent > self._thresholds['cpu_warning']:
            self.alert_manager.send_alert(
                'warning', 'Elevated CPU Usage',
                f'CPU usage at {resources.cpu_percent:.1f}%', 'cpu'
            )
        
        # Memory alerts
        if resources.memory_percent > self._thresholds['memory_critical']:
            self.alert_manager.send_alert(
                'critical', 'Critical Memory Usage',
                f'Memory usage at {resources.memory_percent:.1f}%', 'memory'
            )
        elif resources.memory_percent > self._thresholds['memory_warning']:
            self.alert_manager.send_alert(
                'warning', 'High Memory Usage',
                f'Memory usage at {resources.memory_percent:.1f}%', 'memory'
            )
        
        # Disk alerts
        if resources.disk_used_percent > self._thresholds['disk_critical']:
            self.alert_manager.send_alert(
                'critical', 'Disk Space Critical',
                f'Disk usage at {resources.disk_used_percent:.1f}%', 'disk'
            )
        elif resources.disk_used_percent > self._thresholds['disk_warning']:
            self.alert_manager.send_alert(
                'warning', 'Low Disk Space',
                f'Disk usage at {resources.disk_used_percent:.1f}%', 'disk'
            )
        
        # Temperature alerts
        if resources.temperature_c:
            if resources.temperature_c > self._thresholds['temperature_critical']:
                self.alert_manager.send_alert(
                    'critical', 'Critical Temperature',
                    f'CPU temperature at {resources.temperature_c:.1f}°C', 'temperature'
                )
            elif resources.temperature_c > self._thresholds['temperature_warning']:
                self.alert_manager.send_alert(
                    'warning', 'High Temperature',
                    f'CPU temperature at {resources.temperature_c:.1f}°C', 'temperature'
                )
        
        # Load average alerts
        if resources.load_average[0] > self._thresholds['load_critical']:
            self.alert_manager.send_alert(
                'critical', 'High System Load',
                f'Load average: {resources.load_average[0]:.2f}', 'load'
            )
        elif resources.load_average[0] > self._thresholds['load_warning']:
            self.alert_manager.send_alert(
                'warning', 'Elevated System Load',
                f'Load average: {resources.load_average[0]:.2f}', 'load'
            )
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature (Raspberry Pi specific)"""
        try:
            temp_file = Path('/sys/class/thermal/thermal_zone0/temp')
            if temp_file.exists():
                temp_str = temp_file.read_text().strip()
                return float(temp_str) / 1000.0
        except Exception:
            pass
        return None
    
    def _get_gpu_memory(self) -> Optional[float]:
        """Get GPU memory usage"""
        try:
            result = subprocess.run(['vcgencmd', 'get_mem', 'gpu'], 
                                  capture_output=True, text=True, timeout=1)
            if result.returncode == 0:
                gpu_mem_str = result.stdout.strip().split('=')[1].rstrip('M')
                return float(gpu_mem_str)
        except Exception:
            pass
        return None
    
    def get_system_report(self) -> Dict[str, Any]:
        """Generate comprehensive system report"""
        current_resources = self.get_current_resources()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_resources': asdict(current_resources),
            'top_processes': [asdict(p) for p in self.process_monitor.get_top_processes()],
            'disk_usage': self.disk_monitor.get_disk_usage(),
            'network_stats': self.network_monitor.get_network_stats(),
            'recent_alerts': self.alert_manager.get_alert_history(10),
            'thresholds': self._thresholds,
            'history_size': len(self._resource_history)
        }