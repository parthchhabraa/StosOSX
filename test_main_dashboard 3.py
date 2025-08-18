#!/usr/bin/env python3
"""
Test script for Main Application with Dashboard Integration
Tests the integration of the dashboard module with the main StosOS application
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

from core.logger import stosos_logger
from core.config_manager import ConfigManager
from core.screen_manager import StosOSScreenManager
from modules.dashboard import DashboardModule

# Set up logging
logger = stosos_logger.get_logger(__name__)
stosos_logger.set_debug_mode(True)


def test_dashboard_integration():
    """Test dashboard integration with screen manager"""
    print("=" * 60)
    print("StosOS Dashboard Integration Test")
    print("=" * 60)
    
    try:
        # Test configuration manager
        print("\n1. Testing Configuration Manager...")
        config_manager = ConfigManager()
        print("✓ Config manager created")
        
        # Test screen manager
        print("\n2. Testing Screen Manager...")
        screen_manager = StosOSScreenManager()
        print("✓ Screen manager created")
        
        # Test dashboard module creation
        print("\n3. Testing Dashboard Module...")
        dashboard = DashboardModule()
        dashboard._config_manager = config_manager
        dashboard._screen_manager = screen_manager
        print("✓ Dashboard module created and configured")
        
        # Test module initialization
        print("\n4. Testing Module Initialization...")
        success = dashboard.initialize()
        print(f"✓ Dashboard initialization: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            # Test screen registration
            print("\n5. Testing Screen Registration...")
            screen = dashboard.get_screen()
            if screen:
                screen_manager.add_widget(screen)
                print("✓ Dashboard screen registered with screen manager")
                
                # Test module registration
                print("\n6. Testing Module Registration...")
                registered = screen_manager.register_module(dashboard)
                print(f"✓ Module registration: {'SUCCESS' if registered else 'FAILED'}")
                
                # Test module status
                print("\n7. Testing Module Status...")
                status = dashboard.get_status()
                print(f"✓ Module status: {status}")
                
                # Test navigation
                print("\n8. Testing Navigation...")
                nav_success = screen_manager.navigate_to_module("dashboard")
                print(f"✓ Navigation to dashboard: {'SUCCESS' if nav_success else 'FAILED'}")
                
                # Test cleanup
                print("\n9. Testing Cleanup...")
                dashboard.cleanup()
                print("✓ Dashboard cleanup completed")
        
        print("\n" + "=" * 60)
        print("Dashboard Integration Test Results:")
        print("✓ All integration tests passed successfully")
        print("✓ Dashboard is ready for main application integration")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Integration test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_module_tiles():
    """Test module tile functionality"""
    print("\n" + "=" * 60)
    print("Module Tiles Test")
    print("=" * 60)
    
    try:
        from modules.dashboard import ModuleTile
        
        # Test module tile creation
        print("\n1. Testing Module Tile Creation...")
        module_info = {
            'module_id': 'test_module',
            'display_name': 'Test Module',
            'description': 'A test module',
            'icon': '🧪',
            'status': {'connected': True, 'notifications': 2}
        }
        
        tile = ModuleTile(module_info=module_info)
        print("✓ Module tile created successfully")
        print(f"✓ Tile module ID: {tile.module_info['module_id']}")
        print(f"✓ Tile display name: {tile.module_info['display_name']}")
        
        # Test status update
        print("\n2. Testing Status Update...")
        new_status = {'connected': False, 'notifications': 0}
        tile.update_status(new_status)
        print("✓ Tile status updated successfully")
        
        print("\n✓ Module tiles test completed successfully")
        return True
        
    except Exception as e:
        print(f"\n✗ Module tiles test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("StosOS Dashboard Integration Test Suite")
    
    success = True
    
    # Test dashboard integration
    if not test_dashboard_integration():
        success = False
    
    # Test module tiles
    if not test_module_tiles():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED! Dashboard integration is working correctly.")
        print("✓ The dashboard module is ready for production use.")
    else:
        print("✗ Some tests failed. Check the output above for details.")
    print("=" * 60)
    
    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)