#!/usr/bin/env python3
"""
Minimal test app for branding screen
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

from ui.branding_screen import BrandingScreenManager


class TestBrandingApp(App):
    """Test app for branding screen"""
    
    def build(self):
        """Build the test app"""
        self.root_widget = FloatLayout()
        self.branding_manager = BrandingScreenManager()
        
        # Start branding after a short delay
        Clock.schedule_once(self.start_branding, 0.5)
        
        return self.root_widget
    
    def start_branding(self, dt):
        """Start the branding sequence"""
        print("Starting branding sequence...")
        self.branding_manager.show_branding(
            self.root_widget,
            on_complete=self.on_branding_complete
        )
    
    def on_branding_complete(self):
        """Handle branding completion"""
        print("Branding sequence completed!")
        # In a real app, this would transition to the main interface


if __name__ == '__main__':
    print("Starting branding test app...")
    TestBrandingApp().run()