"""
Base Module Interface for StosOS
All feature modules inherit from this base class
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from kivy.uix.screenmanager import Screen
from kivy.event import EventDispatcher


class BaseModule(ABC, EventDispatcher):
    """Abstract base class for all StosOS modules"""
    
    def __init__(self, module_id: str, display_name: str, icon: str = ""):
        super().__init__()
        self.module_id = module_id
        self.display_name = display_name
        self.icon = icon
        self.screen_widget = None
        self._initialized = False
        self._active = False
        self.logger = logging.getLogger(f"stosos.modules.{module_id}")
        
        # Register events
        self.register_event_type('on_error')
        self.register_event_type('on_status_change')
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the module
        Returns True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_screen(self) -> Screen:
        """
        Get the Kivy Screen widget for this module
        Returns the main screen widget for the module
        """
        pass
    
    def on_activate(self) -> None:
        """
        Called when the module becomes active/visible
        Override to implement module-specific activation logic
        """
        self._active = True
        self.logger.debug(f"Module {self.module_id} activated")
        self.dispatch('on_status_change', {'active': True})
    
    def on_deactivate(self) -> None:
        """
        Called when the module becomes inactive/hidden
        Override to implement module-specific deactivation logic
        """
        self._active = False
        self.logger.debug(f"Module {self.module_id} deactivated")
        self.dispatch('on_status_change', {'active': False})
    
    def handle_voice_command(self, command: str) -> bool:
        """
        Handle voice command directed to this module
        Returns True if command was handled, False otherwise
        """
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current module status information
        Returns dictionary with status information
        """
        return {
            "module_id": self.module_id,
            "display_name": self.display_name,
            "initialized": self._initialized,
            "active": self._active,
            "icon": self.icon
        }
    
    def cleanup(self) -> None:
        """
        Cleanup module resources
        Override to implement module-specific cleanup
        """
        self._initialized = False
        self._active = False
        self.logger.debug(f"Module {self.module_id} cleaned up")
    
    def restart(self) -> bool:
        """
        Restart the module (cleanup and reinitialize)
        Returns True if restart successful, False otherwise
        """
        try:
            self.logger.info(f"Restarting module {self.module_id}")
            
            # Cleanup current state
            self.cleanup()
            
            # Reinitialize
            success = self.initialize()
            
            if success:
                self.logger.info(f"Module {self.module_id} restarted successfully")
                self.dispatch('on_status_change', {'restarted': True, 'success': True})
            else:
                self.logger.error(f"Failed to restart module {self.module_id}")
                self.dispatch('on_status_change', {'restarted': True, 'success': False})
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error during module restart: {e}")
            self.handle_error(e, "module_restart")
            return False
    
    def enable_fallback_mode(self) -> bool:
        """
        Enable fallback mode for graceful degradation
        Override to implement module-specific fallback behavior
        """
        self.logger.info(f"Enabling fallback mode for module {self.module_id}")
        
        # Default fallback: disable non-essential features
        # Modules should override this for specific fallback behavior
        
        self.dispatch('on_status_change', {'fallback_mode': True})
        return True
    
    def disable_fallback_mode(self) -> bool:
        """
        Disable fallback mode and restore full functionality
        """
        self.logger.info(f"Disabling fallback mode for module {self.module_id}")
        
        try:
            # Attempt to restore full functionality
            success = self.initialize()
            
            if success:
                self.dispatch('on_status_change', {'fallback_mode': False})
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to disable fallback mode: {e}")
            self.handle_error(e, "disable_fallback_mode")
            return False
    
    def handle_error(self, error: Exception, context: str = "", 
                    error_type=None, severity=None, 
                    recovery_action=None) -> bool:
        """
        Handle module-specific errors with enhanced error handling
        """
        from core.error_handler import error_handler, ErrorType, ErrorSeverity
        
        # Determine error type if not provided
        if error_type is None:
            error_name = type(error).__name__.lower()
            if 'network' in error_name or 'connection' in error_name:
                error_type = ErrorType.NETWORK
            elif 'permission' in error_name:
                error_type = ErrorType.PERMISSION
            elif 'timeout' in error_name:
                error_type = ErrorType.TIMEOUT
            elif 'memory' in error_name:
                error_type = ErrorType.MEMORY
            else:
                error_type = ErrorType.MODULE
        
        # Determine severity if not provided
        if severity is None:
            if isinstance(error, (ConnectionError, TimeoutError)):
                severity = ErrorSeverity.HIGH
            elif isinstance(error, (PermissionError, FileNotFoundError)):
                severity = ErrorSeverity.MEDIUM
            else:
                severity = ErrorSeverity.MEDIUM
        
        # Use centralized error handler
        success = error_handler.handle_error(
            error=error,
            context=f"{self.module_id}:{context}" if context else self.module_id,
            error_type=error_type,
            severity=severity,
            module_id=self.module_id,
            recovery_action=recovery_action
        )
        
        # Dispatch module-specific error event
        error_info = {
            'module_id': self.module_id,
            'error': str(error),
            'context': context,
            'error_type': type(error).__name__,
            'handled': success
        }
        self.dispatch('on_error', error_info)
        
        return success
    
    def on_error(self, error_info: Dict[str, Any]) -> None:
        """
        Event handler for module errors
        Override to implement custom error handling
        """
        pass
    
    def on_status_change(self, status: Dict[str, Any]) -> None:
        """
        Event handler for status changes
        Override to implement custom status change handling
        """
        pass