"""
Test Module for StosOS Framework
Simple module implementation to test the core framework
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from .base_module import BaseModule


class TestModule(BaseModule):
    """Simple test module to verify framework functionality"""
    
    def __init__(self):
        super().__init__(
            module_id="test_module",
            display_name="Test Module",
            icon="test"
        )
        self.screen = None
    
    def initialize(self) -> bool:
        """Initialize the test module"""
        try:
            self.logger.info("Initializing test module")
            
            # Create the screen layout
            layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
            
            # Add title
            title = Label(
                text='Test Module',
                font_size='24sp',
                size_hint_y=None,
                height=50
            )
            layout.add_widget(title)
            
            # Add status label
            self.status_label = Label(
                text='Module Status: Initialized',
                font_size='16sp',
                size_hint_y=None,
                height=40
            )
            layout.add_widget(self.status_label)
            
            # Add test button
            test_button = Button(
                text='Test Voice Command',
                size_hint_y=None,
                height=50
            )
            test_button.bind(on_press=self._on_test_button)
            layout.add_widget(test_button)
            
            # Create screen
            self.screen = Screen()
            self.screen.add_widget(layout)
            
            self._initialized = True
            self.logger.info("Test module initialized successfully")
            return True
            
        except Exception as e:
            self.handle_error(e, "Test module initialization")
            return False
    
    def get_screen(self) -> Screen:
        """Get the module's screen"""
        return self.screen
    
    def on_activate(self) -> None:
        """Called when module becomes active"""
        super().on_activate()
        if hasattr(self, 'status_label'):
            self.status_label.text = 'Module Status: Active'
    
    def on_deactivate(self) -> None:
        """Called when module becomes inactive"""
        super().on_deactivate()
        if hasattr(self, 'status_label'):
            self.status_label.text = 'Module Status: Inactive'
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice commands for this module"""
        command_lower = command.lower()
        
        if 'test' in command_lower:
            self.logger.info(f"Test module received voice command: {command}")
            if hasattr(self, 'status_label'):
                self.status_label.text = f'Voice Command: {command}'
            return True
        
        return False
    
    def _on_test_button(self, instance):
        """Handle test button press"""
        self.logger.info("Test button pressed")
        test_command = "test voice command"
        self.handle_voice_command(test_command)