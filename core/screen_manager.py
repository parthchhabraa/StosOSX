"""
Enhanced Screen Manager for StosOS
Handles navigation, transitions, and module switching
"""

import logging
from typing import Dict, Optional, Callable
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.animation import Animation
from kivy.clock import Clock

from .base_module import BaseModule


class StosOSScreenManager(ScreenManager):
    """Enhanced screen manager with module integration and smooth transitions"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(__name__)
        self.modules: Dict[str, BaseModule] = {}
        self.transition_callbacks: Dict[str, Callable] = {}
        
        # Set default transition
        self.transition = SlideTransition(direction='left', duration=0.3)
        
        # Navigation history for back functionality
        self.navigation_history = []
        self.max_history = 10
    
    def register_module(self, module: BaseModule) -> bool:
        """
        Register a module with the screen manager
        
        Args:
            module: BaseModule instance to register
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            if not module.initialize():
                self.logger.error(f"Failed to initialize module: {module.module_id}")
                return False
            
            # Get the screen from the module
            screen = module.get_screen()
            if not isinstance(screen, Screen):
                self.logger.error(f"Module {module.module_id} did not return a valid Screen")
                return False
            
            # Set screen name to module ID
            screen.name = module.module_id
            
            # Add screen to manager
            self.add_widget(screen)
            
            # Register module
            self.modules[module.module_id] = module
            
            # Bind module events
            module.bind(on_error=self._on_module_error)
            module.bind(on_status_change=self._on_module_status_change)
            
            self.logger.info(f"Module registered successfully: {module.module_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register module {module.module_id}: {e}")
            return False
    
    def unregister_module(self, module_id: str) -> bool:
        """
        Unregister a module from the screen manager
        
        Args:
            module_id: ID of the module to unregister
            
        Returns:
            bool: True if unregistration successful, False otherwise
        """
        try:
            if module_id not in self.modules:
                self.logger.warning(f"Module not found for unregistration: {module_id}")
                return False
            
            module = self.modules[module_id]
            
            # Cleanup module
            module.cleanup()
            
            # Remove screen
            screen = self.get_screen(module_id)
            if screen:
                self.remove_widget(screen)
            
            # Remove from modules
            del self.modules[module_id]
            
            # Clean navigation history
            self.navigation_history = [screen_name for screen_name in self.navigation_history 
                                     if screen_name != module_id]
            
            self.logger.info(f"Module unregistered successfully: {module_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister module {module_id}: {e}")
            return False
    
    def navigate_to_module(self, module_id: str, transition_type: str = 'slide', 
                          direction: str = 'left', callback: Optional[Callable] = None) -> bool:
        """
        Navigate to a specific module with transition
        
        Args:
            module_id: ID of the module to navigate to
            transition_type: Type of transition ('slide', 'fade', 'none')
            direction: Direction for slide transition ('left', 'right', 'up', 'down')
            callback: Optional callback to execute after transition
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            if module_id not in self.modules:
                self.logger.error(f"Module not found: {module_id}")
                return False
            
            # Deactivate current module if any
            current_module_id = self.current_screen.name if self.current_screen else None
            if current_module_id and current_module_id in self.modules:
                self.modules[current_module_id].on_deactivate()
            
            # Set transition
            self._set_transition(transition_type, direction)
            
            # Store callback if provided
            if callback:
                self.transition_callbacks[module_id] = callback
            
            # Add to navigation history
            if current_module_id and current_module_id != module_id:
                self._add_to_history(current_module_id)
            
            # Switch to module screen
            self.current = module_id
            
            # Activate new module
            self.modules[module_id].on_activate()
            
            # Schedule callback execution after transition
            if callback:
                Clock.schedule_once(lambda dt: self._execute_callback(module_id), 
                                  self.transition.duration + 0.1)
            
            self.logger.debug(f"Navigated to module: {module_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to module {module_id}: {e}")
            return False
    
    def go_back(self) -> bool:
        """
        Navigate back to the previous screen in history
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        if not self.navigation_history:
            self.logger.debug("No navigation history available")
            return False
        
        previous_screen = self.navigation_history.pop()
        return self.navigate_to_module(previous_screen, transition_type='slide', direction='right')
    
    def get_module(self, module_id: str) -> Optional[BaseModule]:
        """
        Get a registered module by ID
        
        Args:
            module_id: ID of the module to retrieve
            
        Returns:
            BaseModule instance or None if not found
        """
        return self.modules.get(module_id)
    
    def get_all_modules(self) -> Dict[str, BaseModule]:
        """
        Get all registered modules
        
        Returns:
            Dictionary of all registered modules
        """
        return self.modules.copy()
    
    def get_module_status(self, module_id: str) -> Optional[Dict]:
        """
        Get status of a specific module
        
        Args:
            module_id: ID of the module
            
        Returns:
            Status dictionary or None if module not found
        """
        module = self.modules.get(module_id)
        return module.get_status() if module else None
    
    def _set_transition(self, transition_type: str, direction: str) -> None:
        """Set the transition type and direction"""
        if transition_type == 'slide':
            self.transition = SlideTransition(direction=direction, duration=0.3)
        elif transition_type == 'fade':
            self.transition = FadeTransition(duration=0.2)
        else:  # 'none' or any other value
            self.transition.duration = 0
    
    def _add_to_history(self, screen_name: str) -> None:
        """Add screen to navigation history"""
        if screen_name in self.navigation_history:
            self.navigation_history.remove(screen_name)
        
        self.navigation_history.append(screen_name)
        
        # Limit history size
        if len(self.navigation_history) > self.max_history:
            self.navigation_history.pop(0)
    
    def _execute_callback(self, module_id: str) -> None:
        """Execute transition callback if exists"""
        callback = self.transition_callbacks.pop(module_id, None)
        if callback:
            try:
                callback()
            except Exception as e:
                self.logger.error(f"Transition callback error for {module_id}: {e}")
    
    def _on_module_error(self, module: BaseModule, error_info: Dict) -> None:
        """Handle module error events"""
        self.logger.error(f"Module error from {error_info['module_id']}: {error_info['error']}")
        # Could implement error recovery logic here
    
    def _on_module_status_change(self, module: BaseModule, status: Dict) -> None:
        """Handle module status change events"""
        self.logger.debug(f"Module {module.module_id} status changed: {status}")