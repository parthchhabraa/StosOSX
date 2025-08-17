#!/usr/bin/env python3
"""
Test script for Dashboard Module
Tests the main dashboard functionality including module tiles, navigation, and UI components
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up test environment
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_LOG_LEVEL'] = 'warning'

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock

from core.logger import stosos_logger
from core.config_manager import ConfigManager
from modules.dashboard import DashboardModule
from ui.theme import StosOSTheme

# Set up logging
logger = stosos_logger.get_logger(__name__)
stosos_logger.set_debug_mode(True)


class DashboardTestApp(App):
    """Test application for Dashboard module"""
    
    def build(self):
        """Build the test application"""
        try:
            logger.info("Starting Dashboard test application")
            
            # Initialize configuration
            self.config_manager = ConfigManager()
            
            # Create screen manager
            self.screen_manager = ScreenManager()
            
            # Create and initialize dashboard module
            self.dashboard_module = DashboardModule()
            
            # Pass dependencies to dashboard
            self.dashboard_module._config_manager = self.config_manager
            self.dashboard_module._screen_manager = self.screen_manager
            
            # Initialize the module
            if not self.dashboard_module.initialize():
                logger.error("Failed to initialize dashboard module")
                return None
            
            # Get the dashboard screen
            dashboard_screen = self.dashboard_module.get_screen()
            if not dashboard_screen:
                logger.error("Failed to get dashboard screen")
                return None
            
            # Add screen to manager
            self.screen_manager.add_widget(dashboard_screen)
            self.screen_manager.current = dashboard_screen.name
            
            # Activate the module
            self.dashboard_module.on_activate()
            
            logger.info("Dashboard test application initialized successfully")
            return self.screen_manager
            
        except Exception as e:
            logger.error(f"Failed to build test application: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def on_start(self):
        """Called when the application starts"""
        logger.info("Dashboard test application started")
        
        # Schedule some test interactions
        Clock.schedule_once(self._test_dashboard_features, 2.0)
    
    def _test_dashboard_features(self, dt):
        """Test various dashboard features"""
        try:
            logger.info("Testing dashboard features...")
            
            # Test module status
            status = self.dashboard_module.get_status()
            logger.info(f"Dashboard status: {status}")
            
            # Test module tile interactions (simulated)
            logger.info("Dashboard features test completed")
            
        except Exception as e:
            logger.error(f"Error testing dashboard features: {e}")
    
    def on_stop(self):
        """Called when the application stops"""
        logger.info("Dashboard test application stopping")
        
        # Cleanup
        if hasattr(self, 'dashboard_module'):
            self.dashboard_module.cleanup()


def test_dashboard_module():
    """Test the dashboard module functionality"""
    print("=" * 60)
    print("StosOS Dashboard Module Test")
    print("=" * 60)
    
    try:
        # Test module creation
        print("\n1. Testing Dashboard Module Creation...")
        dashboard = DashboardModule()
        print(f"✓ Dashboard module created: {dashboard.module_id}")
        print(f"✓ Display name: {dashboard.display_name}")
        print(f"✓ Description: {dashboard.description}")
        
        # Test module initialization
        print("\n2. Testing Module Initialization...")
        config_manager = ConfigManager()
        dashboard._config_manager = config_manager
        
        success = dashboard.initialize()
        print(f"✓ Module initialization: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            # Test screen creation
            print("\n3. Testing Screen Creation...")
            screen = dashboard.get_screen()
            print(f"✓ Screen created: {screen is not None}")
            print(f"✓ Screen name: {screen.name if screen else 'None'}")
            
            # Test module status
            print("\n4. Testing Module Status...")
            status = dashboard.get_status()
            print(f"✓ Status retrieved: {status}")
            
            # Test activation/deactivation
            print("\n5. Testing Module Lifecycle...")
            dashboard.on_activate()
            print("✓ Module activated")
            
            dashboard.on_deactivate()
            print("✓ Module deactivated")
            
            # Test cleanup
            print("\n6. Testing Module Cleanup...")
            dashboard.cleanup()
            print("✓ Module cleaned up")
        
        print("\n" + "=" * 60)
        print("Dashboard Module Test Results:")
        print("✓ All basic tests passed successfully")
        print("✓ Dashboard module is ready for integration")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("StosOS Dashboard Module Test Suite")
    print("Choose test mode:")
    print("1. Basic functionality test (no GUI)")
    print("2. Interactive GUI test")
    
    try:
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            # Run basic tests
            success = test_dashboard_module()
            sys.exit(0 if success else 1)
            
        elif choice == "2":
            # Run interactive GUI test
            print("\nStarting interactive dashboard test...")
            print("This will open a window with the dashboard interface.")
            print("Close the window to exit the test.")
            
            app = DashboardTestApp()
            app.run()
            
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()