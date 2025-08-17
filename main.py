#!/usr/bin/env python3
"""
StosOS Desktop Environment
Main application entry point
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Initialize logging first
from core.logger import stosos_logger
logger = stosos_logger.get_logger(__name__)

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

from core.config_manager import ConfigManager
from core.base_module import BaseModule
from core.screen_manager import StosOSScreenManager
from core.error_handler import error_handler, ErrorType, ErrorSeverity
from core.power_manager import power_manager, PowerConfig
from core.test_module import TestModule
from modules.ui_demo import UIDemoModule
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations
from ui.branding_screen import BrandingScreenManager


class StosOSApp(App):
    """Main StosOS Application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_manager = None
        self.screen_manager = None
        self.module_registry = {}
        self.error_handler = error_handler
        self.branding_manager = BrandingScreenManager()
        self.main_interface_ready = False
        self.power_manager = power_manager
        
    def build(self):
        """Build the main application interface"""
        try:
            logger.info("Starting StosOS Desktop Environment")
            
            # Initialize configuration
            self.config_manager = ConfigManager()
            
            # Set debug mode based on config
            debug_mode = self.config_manager.get('app.debug', False)
            stosos_logger.set_debug_mode(debug_mode)
            
            # Create enhanced screen manager
            self.screen_manager = StosOSScreenManager()
            
            # Initialize power management
            self._initialize_power_management()
            
            # Create main screen with theme (will be shown after branding)
            self._create_main_interface()
            
            # Create branding container that will hold the branding screen
            self.branding_container = Screen(name='branding')
            
            # Apply theme background to branding container
            from kivy.graphics import Color, Rectangle
            with self.branding_container.canvas.before:
                Color(*StosOSTheme.get_color('background'))
                self.branding_bg_rect = Rectangle(
                    pos=self.branding_container.pos, 
                    size=self.branding_container.size
                )
            
            self.branding_container.bind(
                pos=lambda instance, value: setattr(self.branding_bg_rect, 'pos', value),
                size=lambda instance, value: setattr(self.branding_bg_rect, 'size', value)
            )
            
            # Add branding container to screen manager
            self.screen_manager.add_widget(self.branding_container)
            
            # Set branding as current screen
            self.screen_manager.current = 'branding'
            
            logger.info("Application initialized successfully")
            return self.screen_manager
            
        except Exception as e:
            self.error_handler.handle_error(
                e, "Application build", ErrorType.SYSTEM, ErrorSeverity.CRITICAL
            )
            raise
    
    def _create_main_interface(self):
        """Create the main application interface"""
        try:
            # Create main screen with theme
            self.main_screen = Screen(name='main')
            
            # Apply theme background
            from kivy.graphics import Color, Rectangle
            with self.main_screen.canvas.before:
                Color(*StosOSTheme.get_color('background'))
                self.main_bg_rect = Rectangle(
                    pos=self.main_screen.pos, 
                    size=self.main_screen.size
                )
            
            self.main_screen.bind(
                pos=lambda instance, value: setattr(self.main_bg_rect, 'pos', value),
                size=lambda instance, value: setattr(self.main_bg_rect, 'size', value)
            )
            
            # Styled main interface label (temporary)
            main_label = Label(
                text='StosOS X\nMain Interface Ready',
                font_size=str(StosOSTheme.get_font_size('display')) + 'sp',
                color=StosOSTheme.get_color('text_primary'),
                halign='center'
            )
            self.main_screen.add_widget(main_label)
            
            # Add main screen to screen manager (but don't show yet)
            self.screen_manager.add_widget(self.main_screen)
            
            logger.info("Main interface created")
            
        except Exception as e:
            logger.error(f"Failed to create main interface: {e}")
            raise

    def _initialize_power_management(self):
        """Initialize power management system"""
        try:
            # Configure power management based on app config
            power_config = PowerConfig(
                dim_timeout=self.config_manager.get('power.dim_timeout', 30.0),
                sleep_timeout=self.config_manager.get('power.sleep_timeout', 60.0),
                active_brightness=self.config_manager.get('power.active_brightness', 100),
                dimmed_brightness=self.config_manager.get('power.dimmed_brightness', 20),
                sleep_brightness=self.config_manager.get('power.sleep_brightness', 0),
                enable_voice_wake=self.config_manager.get('power.enable_voice_wake', True),
                enable_network_wake=self.config_manager.get('power.enable_network_wake', True)
            )
            
            # Update power manager configuration
            self.power_manager.config = power_config
            
            # Set up touch event handling for the entire app
            self.bind(on_touch_down=self._on_touch_event)
            self.bind(on_touch_move=self._on_touch_event)
            self.bind(on_touch_up=self._on_touch_event)
            
            logger.info("Power management initialized")
            
        except Exception as e:
            self.error_handler.handle_error(
                e, "Power management initialization", ErrorType.SYSTEM, ErrorSeverity.HIGH
            )
    
    def _on_touch_event(self, instance, touch):
        """Handle touch events for power management"""
        try:
            # Create touch data for power manager
            touch_data = {
                'pos': touch.pos,
                'time': touch.time_start if hasattr(touch, 'time_start') else None,
                'is_double_tap': touch.is_double_tap if hasattr(touch, 'is_double_tap') else False
            }
            
            # Notify power manager of touch activity
            self.power_manager.on_touch_event(touch_data)
            
            # Return False to allow normal touch processing
            return False
            
        except Exception as e:
            logger.error(f"Touch event handling error: {e}")
            return False

    def on_start(self):
        """Called when the application starts"""
        try:
            logger.info("Application started - showing branding sequence")
            
            # Start power management monitoring
            self.power_manager.start_monitoring()
            
            # Start branding sequence
            self.branding_manager.show_branding(
                self.branding_container,
                on_complete=self._on_branding_complete
            )
            
        except Exception as e:
            self.error_handler.handle_error(
                e, "Application start", ErrorType.SYSTEM, ErrorSeverity.HIGH
            )
            # Fallback to main interface if branding fails
            self._on_branding_complete()
    
    def _on_branding_complete(self):
        """Called when branding sequence is complete"""
        try:
            logger.info("Branding complete - initializing main interface")
            
            # Initialize modules
            self._initialize_modules()
            
            # Transition to main interface
            self._transition_to_main_interface()
            
        except Exception as e:
            self.error_handler.handle_error(
                e, "Branding completion", ErrorType.SYSTEM, ErrorSeverity.HIGH
            )
    
    def _initialize_modules(self):
        """Initialize and register application modules"""
        try:
            # Register test module to verify framework
            test_module = TestModule()
            if self.register_module(test_module):
                logger.info("Test module registered successfully")
            else:
                logger.error("Failed to register test module")
            
            # Register UI demo module to showcase theme engine
            ui_demo_module = UIDemoModule()
            if self.register_module(ui_demo_module):
                logger.info("UI Demo module registered successfully")
            else:
                logger.error("Failed to register UI demo module")
            
            self.main_interface_ready = True
            
        except Exception as e:
            logger.error(f"Failed to initialize modules: {e}")
            raise
    
    def _transition_to_main_interface(self):
        """Transition from branding to main interface"""
        try:
            # Smooth transition to main screen
            self.screen_manager.transition.direction = 'left'
            self.screen_manager.transition.duration = 0.5
            self.screen_manager.current = 'main'
            
            # Navigate to UI demo to showcase the theme engine
            if self.main_interface_ready:
                from kivy.clock import Clock
                Clock.schedule_once(
                    lambda dt: self.screen_manager.navigate_to_module("ui_demo"), 
                    0.6  # Wait for transition to complete
                )
            
            logger.info("Transitioned to main interface")
            
        except Exception as e:
            logger.error(f"Failed to transition to main interface: {e}")
            # Fallback - just switch screens without animation
            self.screen_manager.current = 'main'
    
    def on_stop(self):
        """Called when the application stops"""
        try:
            logger.info("Application stopping")
            
            # Stop power management
            self.power_manager.stop_monitoring()
            
            # Cleanup all registered modules
            if self.screen_manager:
                for module_id, module in self.screen_manager.get_all_modules().items():
                    try:
                        module.cleanup()
                        logger.debug(f"Cleaned up module: {module_id}")
                    except Exception as e:
                        logger.error(f"Error cleaning up module {module_id}: {e}")
            
        except Exception as e:
            self.error_handler.handle_error(
                e, "Application stop", ErrorType.SYSTEM, ErrorSeverity.MEDIUM
            )
    
    def register_module(self, module: BaseModule) -> bool:
        """
        Register a module with the application
        
        Args:
            module: BaseModule instance to register
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        try:
            if not self.screen_manager:
                logger.error("Screen manager not initialized")
                return False
            
            success = self.screen_manager.register_module(module)
            if success:
                self.module_registry[module.module_id] = module
                logger.info(f"Module registered with application: {module.module_id}")
            
            return success
            
        except Exception as e:
            self.error_handler.handle_error(
                e, f"Module registration: {module.module_id}", 
                ErrorType.MODULE, ErrorSeverity.MEDIUM
            )
            return False
    
    def get_module(self, module_id: str) -> BaseModule:
        """Get a registered module by ID"""
        return self.module_registry.get(module_id)


if __name__ == '__main__':
    # Start the application
    logger.info("Starting StosOS application")
    try:
        StosOSApp().run()
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        sys.exit(1)