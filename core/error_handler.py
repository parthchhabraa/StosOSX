"""
Error Handling System for StosOS
Provides centralized error handling, recovery, and user notification
"""

import logging
import traceback
import threading
import time
import psutil
import os
from enum import Enum
from typing import Dict, Callable, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorType(Enum):
    """Types of errors that can occur"""
    NETWORK = "network"
    HARDWARE = "hardware"
    MODULE = "module"
    SYSTEM = "system"
    API = "api"
    CONFIG = "config"
    USER_INPUT = "user_input"
    MEMORY = "memory"
    DISK = "disk"
    PERMISSION = "permission"
    TIMEOUT = "timeout"


class RecoveryAction(Enum):
    """Types of recovery actions"""
    RETRY = "retry"
    RESTART_MODULE = "restart_module"
    RESTART_SERVICE = "restart_service"
    FALLBACK_MODE = "fallback_mode"
    USER_INTERVENTION = "user_intervention"
    SYSTEM_RESTART = "system_restart"
    IGNORE = "ignore"


class ErrorHandler:
    """Centralized error handling and recovery system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recovery_strategies: Dict[ErrorType, Callable] = {}
        self.error_history = []
        self.max_history = 1000
        
        # Error counters for tracking patterns
        self.error_counts: Dict[str, int] = {}
        
        # Module restart tracking
        self.module_restart_counts: Dict[str, int] = {}
        self.module_restart_times: Dict[str, List[datetime]] = {}
        
        # System health monitoring
        self.health_monitor = SystemHealthMonitor()
        
        # User notification system
        self.notification_callbacks: List[Callable] = []
        
        # Initialize notification manager integration
        self._setup_notification_integration()
        
        # Recovery action history
        self.recovery_history: List[Dict] = []
        
        # Graceful degradation state
        self.degraded_modules: set = set()
        
        # Setup default recovery strategies
        self._setup_default_strategies()
        
        # Start health monitoring
        self.health_monitor.start_monitoring()
    
    def _setup_notification_integration(self) -> None:
        """Setup integration with notification manager"""
        try:
            from core.notification_manager import notification_manager
            
            # Register error handler as notification callback
            notification_manager.register_ui_callback(self._handle_notification_event)
            
            # Register notification manager for error notifications
            self.register_notification_callback(notification_manager.show_error_notification)
            
        except ImportError:
            self.logger.warning("Notification manager not available")
    
    def _handle_notification_event(self, event_type: str, data: Any) -> None:
        """Handle notification events from notification manager"""
        if event_type == 'notification_dismissed':
            self.logger.debug(f"Notification dismissed: {data.id}")
        elif event_type == 'notification_shown':
            self.logger.debug(f"Notification shown: {data.id}")
    
    def register_recovery_strategy(self, error_type: ErrorType, strategy: Callable) -> None:
        """
        Register a recovery strategy for a specific error type
        
        Args:
            error_type: Type of error this strategy handles
            strategy: Callable that attempts to recover from the error
        """
        self.recovery_strategies[error_type] = strategy
        self.logger.debug(f"Recovery strategy registered for {error_type.value}")
    
    def handle_error(self, error: Exception, context: str = "", 
                    error_type: ErrorType = ErrorType.SYSTEM,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    module_id: str = "",
                    recovery_action: Optional[RecoveryAction] = None) -> bool:
        """
        Handle an error with appropriate logging, recovery, and notification
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            error_type: Type of error for recovery strategy selection
            severity: Severity level of the error
            module_id: ID of the module where error occurred
            recovery_action: Specific recovery action to attempt
            
        Returns:
            bool: True if error was handled successfully, False otherwise
        """
        try:
            # Create error record
            error_record = {
                'timestamp': datetime.now(),
                'error_type': error_type.value,
                'severity': severity.value,
                'module_id': module_id,
                'context': context,
                'error_message': str(error),
                'error_class': type(error).__name__,
                'traceback': traceback.format_exc(),
                'system_info': self._get_system_info()
            }
            
            # Add to history
            self._add_to_history(error_record)
            
            # Update error counts
            error_key = f"{error_type.value}:{type(error).__name__}"
            self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
            
            # Log the error
            self._log_error(error_record)
            
            # Notify users if severity is high enough
            if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
                self._notify_users(error_record)
            
            # Determine recovery action
            if recovery_action is None:
                recovery_action = self._determine_recovery_action(error_type, error, module_id)
            
            # Attempt recovery
            recovery_success = self._execute_recovery_action(
                recovery_action, error_type, error, context, module_id
            )
            
            # Record recovery attempt
            self._record_recovery_attempt(error_record, recovery_action, recovery_success)
            
            # Check for error patterns
            self._check_error_patterns(error_key, module_id)
            
            # Check if module should be degraded
            if not recovery_success and severity == ErrorSeverity.CRITICAL:
                self._consider_module_degradation(module_id)
            
            return recovery_success
            
        except Exception as handler_error:
            # Error in error handler - log and continue
            self.logger.critical(f"Error in error handler: {handler_error}")
            return False
    
    def get_error_history(self, limit: int = 10) -> list:
        """
        Get recent error history
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of recent error records
        """
        return self.error_history[-limit:] if self.error_history else []
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics and patterns
        
        Returns:
            Dictionary with error statistics
        """
        total_errors = len(self.error_history)
        
        # Count by type
        type_counts = {}
        severity_counts = {}
        module_counts = {}
        
        for error in self.error_history:
            error_type = error['error_type']
            severity = error['severity']
            module_id = error['module_id']
            
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if module_id:
                module_counts[module_id] = module_counts.get(module_id, 0) + 1
        
        return {
            'total_errors': total_errors,
            'error_counts': self.error_counts.copy(),
            'type_distribution': type_counts,
            'severity_distribution': severity_counts,
            'module_distribution': module_counts
        }
    
    def clear_error_history(self) -> None:
        """Clear error history and reset counters"""
        self.error_history.clear()
        self.error_counts.clear()
        self.logger.info("Error history cleared")
    
    def _setup_default_strategies(self) -> None:
        """Setup default recovery strategies for common error types"""
        
        def network_recovery(error: Exception, context: str) -> bool:
            """Default network error recovery"""
            self.logger.info("Attempting network error recovery")
            # Could implement network reconnection logic here
            return False
        
        def module_recovery(error: Exception, context: str) -> bool:
            """Default module error recovery"""
            self.logger.info(f"Attempting module error recovery for context: {context}")
            # Could implement module restart logic here
            return False
        
        def hardware_recovery(error: Exception, context: str) -> bool:
            """Default hardware error recovery"""
            self.logger.info("Attempting hardware error recovery")
            # Could implement hardware reinitialization here
            return False
        
        # Register default strategies
        self.recovery_strategies[ErrorType.NETWORK] = network_recovery
        self.recovery_strategies[ErrorType.MODULE] = module_recovery
        self.recovery_strategies[ErrorType.HARDWARE] = hardware_recovery
    
    def _add_to_history(self, error_record: Dict) -> None:
        """Add error record to history"""
        self.error_history.append(error_record)
        
        # Limit history size
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)
    
    def _log_error(self, error_record: Dict) -> None:
        """Log error with appropriate level based on severity"""
        severity = error_record['severity']
        message = (f"Error in {error_record['context']}: "
                  f"{error_record['error_message']} "
                  f"(Type: {error_record['error_type']}, "
                  f"Module: {error_record['module_id']})")
        
        if severity == ErrorSeverity.CRITICAL.value:
            self.logger.critical(message)
        elif severity == ErrorSeverity.HIGH.value:
            self.logger.error(message)
        elif severity == ErrorSeverity.MEDIUM.value:
            self.logger.warning(message)
        else:  # LOW
            self.logger.info(message)
        
        # Log full traceback for debugging
        if error_record['traceback']:
            self.logger.debug(f"Full traceback: {error_record['traceback']}")
    
    def _attempt_recovery(self, error_type: ErrorType, error: Exception, context: str) -> bool:
        """Attempt to recover from error using registered strategy"""
        strategy = self.recovery_strategies.get(error_type)
        
        if strategy:
            try:
                self.logger.info(f"Attempting recovery for {error_type.value} error")
                return strategy(error, context)
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
                return False
        else:
            self.logger.debug(f"No recovery strategy available for {error_type.value}")
            return False
    
    def _check_error_patterns(self, error_key: str, module_id: str = "") -> None:
        """Check for error patterns that might indicate systemic issues"""
        count = self.error_counts[error_key]
        
        # Alert on repeated errors
        if count == 5:
            self.logger.warning(f"Error pattern detected: {error_key} occurred {count} times")
        elif count == 10:
            self.logger.error(f"Frequent error pattern: {error_key} occurred {count} times")
            if module_id:
                self._notify_users({
                    'severity': ErrorSeverity.HIGH.value,
                    'error_message': f"Frequent errors in module {module_id}",
                    'context': 'Pattern Detection'
                })
        elif count >= 20:
            self.logger.critical(f"Critical error pattern: {error_key} occurred {count} times")
            if module_id:
                self._consider_module_degradation(module_id)
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information for error context"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.debug(f"Could not get system info: {e}")
            return {}
    
    def _determine_recovery_action(self, error_type: ErrorType, error: Exception, 
                                 module_id: str) -> RecoveryAction:
        """Determine appropriate recovery action based on error characteristics"""
        
        # Check module restart history
        if module_id and self._should_restart_module(module_id):
            return RecoveryAction.RESTART_MODULE
        
        # Network errors - retry with backoff
        if error_type == ErrorType.NETWORK:
            return RecoveryAction.RETRY
        
        # Memory errors - restart module or system
        if error_type == ErrorType.MEMORY:
            if module_id:
                return RecoveryAction.RESTART_MODULE
            else:
                return RecoveryAction.SYSTEM_RESTART
        
        # Hardware errors - user intervention needed
        if error_type == ErrorType.HARDWARE:
            return RecoveryAction.USER_INTERVENTION
        
        # API errors - retry or fallback
        if error_type == ErrorType.API:
            return RecoveryAction.FALLBACK_MODE
        
        # Default to retry for most errors
        return RecoveryAction.RETRY
    
    def _execute_recovery_action(self, action: RecoveryAction, error_type: ErrorType,
                               error: Exception, context: str, module_id: str) -> bool:
        """Execute the determined recovery action"""
        
        try:
            if action == RecoveryAction.RETRY:
                return self._attempt_recovery(error_type, error, context)
            
            elif action == RecoveryAction.RESTART_MODULE:
                return self._restart_module(module_id)
            
            elif action == RecoveryAction.FALLBACK_MODE:
                return self._enable_fallback_mode(module_id)
            
            elif action == RecoveryAction.USER_INTERVENTION:
                self._request_user_intervention(error, context, module_id)
                return False
            
            elif action == RecoveryAction.IGNORE:
                self.logger.info(f"Ignoring error as per recovery action: {error}")
                return True
            
            else:
                self.logger.warning(f"Unhandled recovery action: {action}")
                return False
                
        except Exception as recovery_error:
            self.logger.error(f"Recovery action {action} failed: {recovery_error}")
            return False
    
    def _should_restart_module(self, module_id: str) -> bool:
        """Check if module should be restarted based on restart history"""
        if not module_id:
            return False
        
        restart_count = self.module_restart_counts.get(module_id, 0)
        restart_times = self.module_restart_times.get(module_id, [])
        
        # Don't restart if already restarted too many times
        if restart_count >= 3:
            return False
        
        # Don't restart if restarted recently (within 5 minutes)
        if restart_times:
            last_restart = restart_times[-1]
            if datetime.now() - last_restart < timedelta(minutes=5):
                return False
        
        return True
    
    def _restart_module(self, module_id: str) -> bool:
        """Restart a specific module"""
        if not module_id:
            return False
        
        try:
            self.logger.info(f"Attempting to restart module: {module_id}")
            
            # Update restart tracking
            self.module_restart_counts[module_id] = self.module_restart_counts.get(module_id, 0) + 1
            if module_id not in self.module_restart_times:
                self.module_restart_times[module_id] = []
            self.module_restart_times[module_id].append(datetime.now())
            
            # Notify users
            self._notify_users({
                'severity': ErrorSeverity.MEDIUM.value,
                'error_message': f"Restarting module {module_id}",
                'context': 'Module Recovery'
            })
            
            # Module restart would be handled by the main application
            # This is a placeholder for the actual restart logic
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restart module {module_id}: {e}")
            return False
    
    def _enable_fallback_mode(self, module_id: str) -> bool:
        """Enable fallback mode for a module"""
        try:
            self.logger.info(f"Enabling fallback mode for module: {module_id}")
            self.degraded_modules.add(module_id)
            
            self._notify_users({
                'severity': ErrorSeverity.MEDIUM.value,
                'error_message': f"Module {module_id} running in fallback mode",
                'context': 'Graceful Degradation'
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to enable fallback mode for {module_id}: {e}")
            return False
    
    def _consider_module_degradation(self, module_id: str) -> None:
        """Consider putting a module into degraded state"""
        if module_id and module_id not in self.degraded_modules:
            restart_count = self.module_restart_counts.get(module_id, 0)
            
            if restart_count >= 2:
                self.logger.warning(f"Module {module_id} has failed multiple times, considering degradation")
                self._enable_fallback_mode(module_id)
    
    def _request_user_intervention(self, error: Exception, context: str, module_id: str) -> None:
        """Request user intervention for error resolution"""
        message = f"User intervention required for {module_id or 'system'}: {str(error)}"
        
        self._notify_users({
            'severity': ErrorSeverity.HIGH.value,
            'error_message': message,
            'context': context,
            'requires_action': True,
            'suggested_actions': self._get_suggested_actions(error, module_id)
        })
    
    def _get_suggested_actions(self, error: Exception, module_id: str) -> List[str]:
        """Get suggested actions for error resolution"""
        suggestions = []
        
        error_type = type(error).__name__
        
        if 'Network' in error_type or 'Connection' in error_type:
            suggestions.extend([
                "Check internet connection",
                "Verify network settings",
                "Restart network interface"
            ])
        
        if 'Permission' in error_type:
            suggestions.extend([
                "Check file permissions",
                "Run with appropriate privileges",
                "Verify user access rights"
            ])
        
        if 'Memory' in error_type:
            suggestions.extend([
                "Close unnecessary applications",
                "Restart the system",
                "Check available memory"
            ])
        
        if module_id:
            suggestions.append(f"Restart the {module_id} module")
        
        return suggestions
    
    def _record_recovery_attempt(self, error_record: Dict, action: RecoveryAction, 
                               success: bool) -> None:
        """Record recovery attempt for analysis"""
        recovery_record = {
            'timestamp': datetime.now(),
            'error_id': id(error_record),
            'action': action.value,
            'success': success,
            'module_id': error_record.get('module_id', ''),
            'error_type': error_record.get('error_type', '')
        }
        
        self.recovery_history.append(recovery_record)
        
        # Limit recovery history size
        if len(self.recovery_history) > 500:
            self.recovery_history.pop(0)
    
    def _notify_users(self, error_info: Dict) -> None:
        """Notify users about errors through registered callbacks"""
        for callback in self.notification_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                self.logger.error(f"Error in notification callback: {e}")
    
    def register_notification_callback(self, callback: Callable) -> None:
        """Register a callback for error notifications"""
        self.notification_callbacks.append(callback)
    
    def unregister_notification_callback(self, callback: Callable) -> None:
        """Unregister a notification callback"""
        if callback in self.notification_callbacks:
            self.notification_callbacks.remove(callback)
    
    def get_module_health_status(self, module_id: str) -> Dict[str, Any]:
        """Get health status for a specific module"""
        restart_count = self.module_restart_counts.get(module_id, 0)
        is_degraded = module_id in self.degraded_modules
        
        # Count recent errors for this module
        recent_errors = 0
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        for error in self.error_history:
            if (error.get('module_id') == module_id and 
                error.get('timestamp', datetime.min) > cutoff_time):
                recent_errors += 1
        
        health_score = 100
        if restart_count > 0:
            health_score -= restart_count * 20
        if is_degraded:
            health_score -= 30
        if recent_errors > 0:
            health_score -= recent_errors * 5
        
        health_score = max(0, health_score)
        
        return {
            'module_id': module_id,
            'health_score': health_score,
            'restart_count': restart_count,
            'is_degraded': is_degraded,
            'recent_errors': recent_errors,
            'status': 'healthy' if health_score > 80 else 'degraded' if health_score > 50 else 'critical'
        }
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """Get comprehensive system health report"""
        return {
            'timestamp': datetime.now(),
            'error_statistics': self.get_error_statistics(),
            'system_metrics': self.health_monitor.get_current_metrics(),
            'degraded_modules': list(self.degraded_modules),
            'recent_recovery_attempts': self.recovery_history[-10:],
            'overall_health': self._calculate_overall_health()
        }
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall system health status"""
        if len(self.degraded_modules) > 2:
            return 'critical'
        elif len(self.degraded_modules) > 0:
            return 'degraded'
        
        recent_errors = len([e for e in self.error_history 
                           if e.get('timestamp', datetime.min) > datetime.now() - timedelta(hours=1)])
        
        if recent_errors > 10:
            return 'degraded'
        elif recent_errors > 5:
            return 'warning'
        else:
            return 'healthy'


class SystemHealthMonitor:
    """Monitor system health metrics and detect issues"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SystemHealthMonitor")
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.max_history = 1440  # 24 hours of minute-by-minute data
        
        # Thresholds for alerts
        self.cpu_threshold = 90.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        self.temperature_threshold = 80.0  # Celsius for Raspberry Pi
    
    def start_monitoring(self) -> None:
        """Start system health monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            self.logger.info("System health monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop system health monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("System health monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Limit history size
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                
                # Check for alerts
                self._check_alerts(metrics)
                
                # Sleep for 60 seconds
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                time.sleep(60)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                'timestamp': datetime.now(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available': memory.available,
                'disk_percent': disk.percent,
                'disk_free': disk.free,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
            # Try to get temperature (Raspberry Pi specific)
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp_raw = f.read().strip()
                    metrics['temperature'] = float(temp_raw) / 1000.0
            except (FileNotFoundError, ValueError, PermissionError):
                metrics['temperature'] = None
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics: {e}")
            return {'timestamp': datetime.now(), 'error': str(e)}
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> None:
        """Check metrics against thresholds and generate alerts"""
        
        # CPU usage alert
        if metrics.get('cpu_percent', 0) > self.cpu_threshold:
            error_handler.handle_error(
                Exception(f"High CPU usage: {metrics['cpu_percent']:.1f}%"),
                context="System Health Monitor",
                error_type=ErrorType.SYSTEM,
                severity=ErrorSeverity.HIGH
            )
        
        # Memory usage alert
        if metrics.get('memory_percent', 0) > self.memory_threshold:
            error_handler.handle_error(
                Exception(f"High memory usage: {metrics['memory_percent']:.1f}%"),
                context="System Health Monitor",
                error_type=ErrorType.MEMORY,
                severity=ErrorSeverity.HIGH
            )
        
        # Disk usage alert
        if metrics.get('disk_percent', 0) > self.disk_threshold:
            error_handler.handle_error(
                Exception(f"High disk usage: {metrics['disk_percent']:.1f}%"),
                context="System Health Monitor",
                error_type=ErrorType.DISK,
                severity=ErrorSeverity.HIGH
            )
        
        # Temperature alert (Raspberry Pi)
        temp = metrics.get('temperature')
        if temp and temp > self.temperature_threshold:
            error_handler.handle_error(
                Exception(f"High temperature: {temp:.1f}°C"),
                context="System Health Monitor",
                error_type=ErrorType.HARDWARE,
                severity=ErrorSeverity.HIGH
            )
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get the most recent metrics"""
        if self.metrics_history:
            return self.metrics_history[-1]
        else:
            return self._collect_metrics()
    
    def get_metrics_history(self, hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history for specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [m for m in self.metrics_history 
                if m.get('timestamp', datetime.min) > cutoff_time]


class DiagnosticTools:
    """Diagnostic tools for troubleshooting common issues"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.DiagnosticTools")
    
    def run_system_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics"""
        results = {
            'timestamp': datetime.now(),
            'tests': {}
        }
        
        # Test network connectivity
        results['tests']['network'] = self._test_network_connectivity()
        
        # Test disk space and permissions
        results['tests']['disk'] = self._test_disk_health()
        
        # Test memory usage
        results['tests']['memory'] = self._test_memory_health()
        
        # Test system services
        results['tests']['services'] = self._test_system_services()
        
        # Test hardware components
        results['tests']['hardware'] = self._test_hardware()
        
        return results
    
    def _test_network_connectivity(self) -> Dict[str, Any]:
        """Test network connectivity"""
        import subprocess
        
        result = {
            'status': 'unknown',
            'details': {},
            'issues': []
        }
        
        try:
            # Test local connectivity
            local_result = subprocess.run(['ping', '-c', '1', '127.0.0.1'], 
                                        capture_output=True, timeout=5)
            result['details']['localhost'] = local_result.returncode == 0
            
            # Test internet connectivity
            internet_result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                           capture_output=True, timeout=10)
            result['details']['internet'] = internet_result.returncode == 0
            
            if not result['details']['localhost']:
                result['issues'].append("Local network interface not responding")
            
            if not result['details']['internet']:
                result['issues'].append("No internet connectivity")
            
            if result['details']['localhost'] and result['details']['internet']:
                result['status'] = 'healthy'
            elif result['details']['localhost']:
                result['status'] = 'degraded'
            else:
                result['status'] = 'critical'
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _test_disk_health(self) -> Dict[str, Any]:
        """Test disk space and permissions"""
        result = {
            'status': 'unknown',
            'details': {},
            'issues': []
        }
        
        try:
            # Check disk usage
            disk_usage = psutil.disk_usage('/')
            result['details']['disk_usage_percent'] = (disk_usage.used / disk_usage.total) * 100
            result['details']['free_space_gb'] = disk_usage.free / (1024**3)
            
            # Check write permissions
            test_file = Path('/tmp/stosos_write_test')
            try:
                test_file.write_text('test')
                test_file.unlink()
                result['details']['write_permission'] = True
            except Exception:
                result['details']['write_permission'] = False
                result['issues'].append("No write permission to temporary directory")
            
            # Check log directory
            log_dir = Path('logs')
            if not log_dir.exists():
                result['issues'].append("Log directory does not exist")
            elif not os.access(log_dir, os.W_OK):
                result['issues'].append("No write permission to log directory")
            
            # Determine status
            if result['details']['disk_usage_percent'] > 95:
                result['status'] = 'critical'
                result['issues'].append("Disk space critically low")
            elif result['details']['disk_usage_percent'] > 85:
                result['status'] = 'degraded'
                result['issues'].append("Disk space running low")
            elif result['issues']:
                result['status'] = 'degraded'
            else:
                result['status'] = 'healthy'
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _test_memory_health(self) -> Dict[str, Any]:
        """Test memory usage and availability"""
        result = {
            'status': 'unknown',
            'details': {},
            'issues': []
        }
        
        try:
            memory = psutil.virtual_memory()
            result['details']['memory_percent'] = memory.percent
            result['details']['available_gb'] = memory.available / (1024**3)
            result['details']['total_gb'] = memory.total / (1024**3)
            
            if memory.percent > 95:
                result['status'] = 'critical'
                result['issues'].append("Memory usage critically high")
            elif memory.percent > 85:
                result['status'] = 'degraded'
                result['issues'].append("Memory usage high")
            else:
                result['status'] = 'healthy'
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _test_system_services(self) -> Dict[str, Any]:
        """Test critical system services"""
        result = {
            'status': 'unknown',
            'details': {},
            'issues': []
        }
        
        try:
            # Check if running as systemd service
            import subprocess
            
            try:
                service_result = subprocess.run(['systemctl', 'is-active', 'stosos'], 
                                             capture_output=True, text=True, timeout=5)
                result['details']['systemd_service'] = service_result.stdout.strip() == 'active'
            except Exception:
                result['details']['systemd_service'] = False
            
            # Check display server
            display_env = os.environ.get('DISPLAY')
            result['details']['display_available'] = display_env is not None
            
            if not result['details']['display_available']:
                result['issues'].append("No display server available")
            
            if result['issues']:
                result['status'] = 'degraded'
            else:
                result['status'] = 'healthy'
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def _test_hardware(self) -> Dict[str, Any]:
        """Test hardware components"""
        result = {
            'status': 'unknown',
            'details': {},
            'issues': []
        }
        
        try:
            # Check temperature
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp_raw = f.read().strip()
                    temperature = float(temp_raw) / 1000.0
                    result['details']['temperature'] = temperature
                    
                    if temperature > 85:
                        result['issues'].append(f"High temperature: {temperature:.1f}°C")
            except Exception:
                result['details']['temperature'] = None
            
            # Check CPU frequency
            try:
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    result['details']['cpu_frequency'] = cpu_freq.current
            except Exception:
                result['details']['cpu_frequency'] = None
            
            if result['issues']:
                result['status'] = 'degraded'
            else:
                result['status'] = 'healthy'
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result


# Global instances
error_handler = ErrorHandler()
diagnostic_tools = DiagnosticTools()