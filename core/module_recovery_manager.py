"""
Module Recovery Manager for StosOS
Handles module-specific error recovery and restart operations
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from enum import Enum

from core.base_module import BaseModule


class ModuleState(Enum):
    """Module operational states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    RESTARTING = "restarting"
    FALLBACK = "fallback"


class ModuleRecoveryManager:
    """Manages module recovery operations and health monitoring"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.modules: Dict[str, BaseModule] = {}
        self.module_states: Dict[str, ModuleState] = {}
        self.recovery_callbacks: Dict[str, List[Callable]] = {}
        
        # Recovery tracking
        self.restart_attempts: Dict[str, int] = {}
        self.last_restart_times: Dict[str, datetime] = {}
        self.recovery_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.max_restart_attempts = 3
        self.restart_cooldown_minutes = 5
        self.health_check_interval = 30  # seconds
        
        # Health monitoring
        self.health_monitor_active = False
        self.health_monitor_thread = None
        
        # Module dependencies
        self.module_dependencies: Dict[str, List[str]] = {}
    
    def register_module(self, module: BaseModule, 
                       dependencies: Optional[List[str]] = None) -> None:
        """
        Register a module for recovery management
        
        Args:
            module: The module instance to register
            dependencies: List of module IDs this module depends on
        """
        module_id = module.module_id
        self.modules[module_id] = module
        self.module_states[module_id] = ModuleState.HEALTHY
        self.recovery_callbacks[module_id] = []
        
        if dependencies:
            self.module_dependencies[module_id] = dependencies
        
        # Bind to module events
        module.bind(on_error=self._on_module_error)
        module.bind(on_status_change=self._on_module_status_change)
        
        self.logger.info(f"Registered module {module_id} for recovery management")
    
    def unregister_module(self, module_id: str) -> None:
        """Unregister a module from recovery management"""
        if module_id in self.modules:
            module = self.modules[module_id]
            module.unbind(on_error=self._on_module_error)
            module.unbind(on_status_change=self._on_module_status_change)
            
            del self.modules[module_id]
            del self.module_states[module_id]
            del self.recovery_callbacks[module_id]
            
            if module_id in self.module_dependencies:
                del self.module_dependencies[module_id]
            
            self.logger.info(f"Unregistered module {module_id}")
    
    def restart_module(self, module_id: str, force: bool = False) -> bool:
        """
        Restart a specific module
        
        Args:
            module_id: ID of the module to restart
            force: Force restart even if cooldown period hasn't elapsed
            
        Returns:
            bool: True if restart was successful, False otherwise
        """
        if module_id not in self.modules:
            self.logger.error(f"Module {module_id} not registered")
            return False
        
        module = self.modules[module_id]
        
        # Check restart limits
        if not force and not self._can_restart_module(module_id):
            self.logger.warning(f"Cannot restart module {module_id}: limits exceeded")
            return False
        
        try:
            self.logger.info(f"Restarting module {module_id}")
            self.module_states[module_id] = ModuleState.RESTARTING
            
            # Update restart tracking
            self.restart_attempts[module_id] = self.restart_attempts.get(module_id, 0) + 1
            self.last_restart_times[module_id] = datetime.now()
            
            # Notify callbacks
            self._notify_recovery_callbacks(module_id, 'restart_started')
            
            # Perform restart
            success = module.restart()
            
            if success:
                self.module_states[module_id] = ModuleState.HEALTHY
                self.logger.info(f"Module {module_id} restarted successfully")
                
                # Reset restart counter on successful restart
                self.restart_attempts[module_id] = 0
                
                # Check dependent modules
                self._check_dependent_modules(module_id)
                
            else:
                self.module_states[module_id] = ModuleState.FAILED
                self.logger.error(f"Module {module_id} restart failed")
                
                # Consider fallback mode
                if self.restart_attempts[module_id] >= self.max_restart_attempts:
                    self._enable_module_fallback(module_id)
            
            # Record recovery attempt
            self._record_recovery_attempt(module_id, 'restart', success)
            
            # Notify callbacks
            self._notify_recovery_callbacks(module_id, 'restart_completed', {'success': success})
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during module restart: {e}")
            self.module_states[module_id] = ModuleState.FAILED
            return False
    
    def enable_module_fallback(self, module_id: str) -> bool:
        """Enable fallback mode for a module"""
        return self._enable_module_fallback(module_id)
    
    def disable_module_fallback(self, module_id: str) -> bool:
        """Disable fallback mode for a module"""
        if module_id not in self.modules:
            return False
        
        module = self.modules[module_id]
        
        try:
            success = module.disable_fallback_mode()
            
            if success:
                self.module_states[module_id] = ModuleState.HEALTHY
                self.logger.info(f"Fallback mode disabled for module {module_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to disable fallback mode for {module_id}: {e}")
            return False
    
    def get_module_health(self, module_id: str) -> Dict[str, Any]:
        """Get health information for a specific module"""
        if module_id not in self.modules:
            return {'error': 'Module not found'}
        
        module = self.modules[module_id]
        state = self.module_states.get(module_id, ModuleState.HEALTHY)
        restart_count = self.restart_attempts.get(module_id, 0)
        last_restart = self.last_restart_times.get(module_id)
        
        return {
            'module_id': module_id,
            'state': state.value,
            'restart_count': restart_count,
            'last_restart': last_restart.isoformat() if last_restart else None,
            'can_restart': self._can_restart_module(module_id),
            'module_status': module.get_status()
        }
    
    def get_all_module_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health information for all registered modules"""
        return {
            module_id: self.get_module_health(module_id)
            for module_id in self.modules.keys()
        }
    
    def start_health_monitoring(self) -> None:
        """Start automatic health monitoring for all modules"""
        if not self.health_monitor_active:
            self.health_monitor_active = True
            self.health_monitor_thread = threading.Thread(
                target=self._health_monitor_loop, 
                daemon=True
            )
            self.health_monitor_thread.start()
            self.logger.info("Module health monitoring started")
    
    def stop_health_monitoring(self) -> None:
        """Stop automatic health monitoring"""
        self.health_monitor_active = False
        if self.health_monitor_thread:
            self.health_monitor_thread.join(timeout=5)
        self.logger.info("Module health monitoring stopped")
    
    def register_recovery_callback(self, module_id: str, callback: Callable) -> None:
        """Register callback for module recovery events"""
        if module_id in self.recovery_callbacks:
            self.recovery_callbacks[module_id].append(callback)
    
    def unregister_recovery_callback(self, module_id: str, callback: Callable) -> None:
        """Unregister recovery callback"""
        if module_id in self.recovery_callbacks and callback in self.recovery_callbacks[module_id]:
            self.recovery_callbacks[module_id].remove(callback)
    
    def get_recovery_history(self, module_id: Optional[str] = None, 
                           limit: int = 20) -> List[Dict[str, Any]]:
        """Get recovery history for a module or all modules"""
        history = self.recovery_history
        
        if module_id:
            history = [r for r in history if r.get('module_id') == module_id]
        
        return history[-limit:] if history else []
    
    def _can_restart_module(self, module_id: str) -> bool:
        """Check if module can be restarted based on limits and cooldown"""
        restart_count = self.restart_attempts.get(module_id, 0)
        
        # Check restart limit
        if restart_count >= self.max_restart_attempts:
            return False
        
        # Check cooldown period
        last_restart = self.last_restart_times.get(module_id)
        if last_restart:
            cooldown_period = timedelta(minutes=self.restart_cooldown_minutes)
            if datetime.now() - last_restart < cooldown_period:
                return False
        
        return True
    
    def _enable_module_fallback(self, module_id: str) -> bool:
        """Enable fallback mode for a module"""
        if module_id not in self.modules:
            return False
        
        module = self.modules[module_id]
        
        try:
            success = module.enable_fallback_mode()
            
            if success:
                self.module_states[module_id] = ModuleState.FALLBACK
                self.logger.info(f"Fallback mode enabled for module {module_id}")
                
                # Notify callbacks
                self._notify_recovery_callbacks(module_id, 'fallback_enabled')
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to enable fallback mode for {module_id}: {e}")
            return False
    
    def _check_dependent_modules(self, recovered_module_id: str) -> None:
        """Check and potentially recover modules that depend on the recovered module"""
        for module_id, dependencies in self.module_dependencies.items():
            if recovered_module_id in dependencies:
                module_state = self.module_states.get(module_id, ModuleState.HEALTHY)
                
                if module_state in [ModuleState.FAILED, ModuleState.FALLBACK]:
                    self.logger.info(f"Attempting to recover dependent module {module_id}")
                    
                    if module_state == ModuleState.FALLBACK:
                        self.disable_module_fallback(module_id)
                    else:
                        self.restart_module(module_id)
    
    def _health_monitor_loop(self) -> None:
        """Main health monitoring loop"""
        while self.health_monitor_active:
            try:
                for module_id, module in self.modules.items():
                    self._check_module_health(module_id, module)
                
                time.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Error in health monitoring: {e}")
                time.sleep(self.health_check_interval)
    
    def _check_module_health(self, module_id: str, module: BaseModule) -> None:
        """Check health of a specific module"""
        try:
            # Get module status
            status = module.get_status()
            
            # Check if module is responsive
            if not status.get('initialized', False):
                current_state = self.module_states.get(module_id, ModuleState.HEALTHY)
                
                if current_state not in [ModuleState.RESTARTING, ModuleState.FAILED]:
                    self.logger.warning(f"Module {module_id} appears uninitialized")
                    self.module_states[module_id] = ModuleState.DEGRADED
            
        except Exception as e:
            self.logger.error(f"Health check failed for module {module_id}: {e}")
            
            current_state = self.module_states.get(module_id, ModuleState.HEALTHY)
            if current_state == ModuleState.HEALTHY:
                self.module_states[module_id] = ModuleState.DEGRADED
    
    def _on_module_error(self, module, error_info: Dict[str, Any]) -> None:
        """Handle module error events"""
        module_id = error_info.get('module_id', '')
        
        if module_id in self.modules:
            current_state = self.module_states.get(module_id, ModuleState.HEALTHY)
            
            # Update module state based on error severity
            if current_state == ModuleState.HEALTHY:
                self.module_states[module_id] = ModuleState.DEGRADED
            elif current_state == ModuleState.DEGRADED:
                self.module_states[module_id] = ModuleState.FAILED
                
                # Consider automatic restart
                if self._can_restart_module(module_id):
                    self.logger.info(f"Automatically restarting failed module {module_id}")
                    self.restart_module(module_id)
    
    def _on_module_status_change(self, module, status_info: Dict[str, Any]) -> None:
        """Handle module status change events"""
        # This can be used to track module state changes
        pass
    
    def _notify_recovery_callbacks(self, module_id: str, event: str, 
                                 data: Optional[Dict[str, Any]] = None) -> None:
        """Notify registered callbacks about recovery events"""
        callbacks = self.recovery_callbacks.get(module_id, [])
        
        for callback in callbacks:
            try:
                callback(module_id, event, data or {})
            except Exception as e:
                self.logger.error(f"Error in recovery callback: {e}")
    
    def _record_recovery_attempt(self, module_id: str, action: str, success: bool) -> None:
        """Record recovery attempt for analysis"""
        record = {
            'timestamp': datetime.now(),
            'module_id': module_id,
            'action': action,
            'success': success,
            'restart_count': self.restart_attempts.get(module_id, 0)
        }
        
        self.recovery_history.append(record)
        
        # Limit history size
        if len(self.recovery_history) > 1000:
            self.recovery_history.pop(0)


# Global module recovery manager instance
module_recovery_manager = ModuleRecoveryManager()