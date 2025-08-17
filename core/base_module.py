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
    
    def handle_error(self, error: Exception, context: str = "") -> None:
        """
        Handle module-specific errors
        """
        error_info = {
            'module_id': self.module_id,
            'error': str(error),
            'context': context,
            'error_type': type(error).__name__
        }
        self.logger.error(f"Module error in {context}: {error}")
        self.dispatch('on_error', error_info)
    
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