#!/usr/bin/env python3
"""
Power Management Demo Module
Demonstrates power management functionality with interactive controls
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

from core.base_module import BaseModule
from core.power_manager import power_manager, PowerState
from ui.theme import StosOSTheme
from ui.components import StosOSButton, StosOSLabel


class PowerDemoModule(BaseModule):
    """Interactive power management demonstration"""
    
    def __init__(self):
        super().__init__(
            module_id="power_demo",
            display_name="Power Management Demo",
            icon="power"
        )
        self.power_manager = power_manager
        self.status_label = None
        self.brightness_label = None
        self.idle_label = None
        self.update_event = None
        self.screen = None
    
    def initialize(self):
        """Initialize the power demo module"""
        try:
            self.logger.info("Initializing power management demo module")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize power demo module: {e}")
            return False
    
    def get_screen(self):
        """Get the module's screen"""
        if not self.screen:
            from kivy.uix.screenmanager import Screen
            self.screen = Screen(name=self.module_id)
            interface = self.create_interface()
            if interface:
                self.screen.add_widget(interface)
        return self.screen
    
    def create_interface(self):
        """Create the power management demo interface"""
        try:
            # Main container
            main_layout = BoxLayout(
                orientation='vertical',
                spacing=20,
                padding=20
            )
            
            # Title
            title = StosOSLabel(
                text='Power Management Demo',
                font_size=str(StosOSTheme.get_font_size('title')) + 'sp',
                size_hint_y=None,
                height=60
            )
            main_layout.add_widget(title)
            
            # Status display
            status_layout = self._create_status_display()
            main_layout.add_widget(status_layout)
            
            # Controls
            controls_layout = self._create_controls()
            main_layout.add_widget(controls_layout)
            
            # Start status updates
            self.update_event = Clock.schedule_interval(self._update_status, 1.0)
            
            return main_layout
            
        except Exception as e:
            self.logger.error(f"Failed to create power demo interface: {e}")
            return Label(text=f"Error: {e}")
    
    def _create_status_display(self):
        """Create status display section"""
        status_container = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None,
            height=200
        )
        
        # Status labels
        self.status_label = StosOSLabel(
            text='Power State: ACTIVE',
            font_size=str(StosOSTheme.get_font_size('body')) + 'sp'
        )
        
        self.brightness_label = StosOSLabel(
            text='Brightness: 100%',
            font_size=str(StosOSTheme.get_font_size('body')) + 'sp'
        )
        
        self.idle_label = StosOSLabel(
            text='Idle Time: 0.0s',
            font_size=str(StosOSTheme.get_font_size('body')) + 'sp'
        )
        
        status_container.add_widget(self.status_label)
        status_container.add_widget(self.brightness_label)
        status_container.add_widget(self.idle_label)
        
        return status_container
    
    def _create_controls(self):
        """Create control buttons and sliders"""
        controls_container = BoxLayout(
            orientation='vertical',
            spacing=15
        )
        
        # Power state controls
        power_controls = GridLayout(
            cols=3,
            spacing=10,
            size_hint_y=None,
            height=60
        )
        
        wake_btn = StosOSButton(
            text='Wake Display',
            on_press=lambda x: self._wake_display()
        )
        
        sleep_btn = StosOSButton(
            text='Force Sleep',
            on_press=lambda x: self._force_sleep()
        )
        
        activity_btn = StosOSButton(
            text='User Activity',
            on_press=lambda x: self._trigger_activity()
        )
        
        power_controls.add_widget(wake_btn)
        power_controls.add_widget(sleep_btn)
        power_controls.add_widget(activity_btn)
        
        # Brightness control
        brightness_container = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=80
        )
        
        brightness_title = StosOSLabel(
            text='Manual Brightness Control',
            font_size=str(StosOSTheme.get_font_size('body')) + 'sp',
            size_hint_y=None,
            height=30
        )
        
        brightness_slider = Slider(
            min=0,
            max=100,
            value=100,
            step=1,
            size_hint_y=None,
            height=40
        )
        brightness_slider.bind(value=self._on_brightness_change)
        
        brightness_container.add_widget(brightness_title)
        brightness_container.add_widget(brightness_slider)
        
        # Configuration display
        config_container = BoxLayout(
            orientation='vertical',
            spacing=5,
            size_hint_y=None,
            height=120
        )
        
        config_title = StosOSLabel(
            text='Power Configuration',
            font_size=str(StosOSTheme.get_font_size('body')) + 'sp',
            size_hint_y=None,
            height=30
        )
        
        config_info = StosOSLabel(
            text=f'Dim Timeout: {self.power_manager.config.dim_timeout}s\n'
                 f'Sleep Timeout: {self.power_manager.config.sleep_timeout}s\n'
                 f'Brightness Method: {self.power_manager._brightness_method}',
            font_size=str(StosOSTheme.get_font_size('caption')) + 'sp',
            size_hint_y=None,
            height=80
        )
        
        config_container.add_widget(config_title)
        config_container.add_widget(config_info)
        
        # Add all sections
        controls_container.add_widget(power_controls)
        controls_container.add_widget(brightness_container)
        controls_container.add_widget(config_container)
        
        return controls_container
    
    def _update_status(self, dt):
        """Update status display"""
        try:
            if self.status_label:
                state = self.power_manager.get_power_state()
                self.status_label.text = f'Power State: {state.value.upper()}'
            
            if self.brightness_label:
                brightness = self.power_manager.get_brightness()
                self.brightness_label.text = f'Brightness: {brightness}%'
            
            if self.idle_label:
                idle_time = self.power_manager.get_idle_time()
                self.idle_label.text = f'Idle Time: {idle_time:.1f}s'
                
        except Exception as e:
            self.logger.error(f"Status update error: {e}")
    
    def _wake_display(self):
        """Wake the display"""
        try:
            self.power_manager.wake_display("demo_button")
            self.logger.info("Display wake triggered from demo")
        except Exception as e:
            self.logger.error(f"Wake display error: {e}")
    
    def _force_sleep(self):
        """Force display to sleep"""
        try:
            self.power_manager.force_sleep()
            self.logger.info("Force sleep triggered from demo")
        except Exception as e:
            self.logger.error(f"Force sleep error: {e}")
    
    def _trigger_activity(self):
        """Trigger user activity"""
        try:
            self.power_manager.on_user_activity()
            self.logger.info("User activity triggered from demo")
        except Exception as e:
            self.logger.error(f"User activity error: {e}")
    
    def _on_brightness_change(self, instance, value):
        """Handle brightness slider change"""
        try:
            brightness = int(value)
            self.power_manager.set_brightness(brightness)
            self.logger.debug(f"Brightness set to {brightness}% from demo")
        except Exception as e:
            self.logger.error(f"Brightness change error: {e}")
    
    def cleanup(self):
        """Clean up the module"""
        try:
            if self.update_event:
                self.update_event.cancel()
                self.update_event = None
            
            super().cleanup()
            self.logger.info("Power demo module cleaned up")
            
        except Exception as e:
            self.logger.error(f"Power demo cleanup error: {e}")