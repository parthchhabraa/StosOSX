#!/usr/bin/env python3
"""
Test script for StosOS core framework
Tests the BaseModule, ScreenManager, ConfigManager, and ErrorHandler
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Initialize logging
from core.logger import stosos_logger
logger = stosos_logger.get_logger(__name__)

from core.config_manager import ConfigManager
from core.screen_manager import StosOSScreenManager
from core.error_handler import error_handler, ErrorType, ErrorSeverity
from core.test_module import TestModule


def test_config_manager():
    """Test ConfigManager functionality"""
    print("\n=== Testing ConfigManager ===")
    
    config = ConfigManager()
    
    # Test getting default values
    app_name = config.get('app.name')
    print(f"App name: {app_name}")
    
    # Test setting and getting values
    config.set('test.value', 'test_data')
    test_value = config.get('test.value')
    print(f"Test value: {test_value}")
    
    # Test API key functionality
    config.set_api_key('test_service', 'test_key_123')
    api_key = config.get_api_key('test_service')
    print(f"API key: {api_key}")
    
    # Test module enabled check
    calendar_enabled = config.is_module_enabled('calendar')
    print(f"Calendar module enabled: {calendar_enabled}")
    
    print("ConfigManager tests completed successfully!")


def test_error_handler():
    """Test ErrorHandler functionality"""
    print("\n=== Testing ErrorHandler ===")
    
    # Test error handling
    try:
        raise ValueError("Test error for framework testing")
    except Exception as e:
        success = error_handler.handle_error(
            e, "Test context", ErrorType.SYSTEM, ErrorSeverity.MEDIUM
        )
        print(f"Error handled successfully: {success}")
    
    # Test error statistics
    stats = error_handler.get_error_statistics()
    print(f"Error statistics: {stats}")
    
    # Test error history
    history = error_handler.get_error_history(limit=1)
    if history:
        print(f"Latest error: {history[-1]['error_message']}")
    
    print("ErrorHandler tests completed successfully!")


def test_base_module():
    """Test BaseModule functionality"""
    print("\n=== Testing BaseModule ===")
    
    # Create test module
    test_module = TestModule()
    
    # Test initialization
    init_success = test_module.initialize()
    print(f"Module initialization: {init_success}")
    
    # Test status
    status = test_module.get_status()
    print(f"Module status: {status}")
    
    # Test voice command handling
    voice_handled = test_module.handle_voice_command("test command")
    print(f"Voice command handled: {voice_handled}")
    
    # Test activation/deactivation
    test_module.on_activate()
    print(f"Module activated, active status: {test_module._active}")
    
    test_module.on_deactivate()
    print(f"Module deactivated, active status: {test_module._active}")
    
    # Test cleanup
    test_module.cleanup()
    print(f"Module cleaned up, initialized status: {test_module._initialized}")
    
    print("BaseModule tests completed successfully!")


def test_screen_manager():
    """Test StosOSScreenManager functionality"""
    print("\n=== Testing StosOSScreenManager ===")
    
    # Create screen manager
    screen_manager = StosOSScreenManager()
    
    # Create and register test module
    test_module = TestModule()
    registration_success = screen_manager.register_module(test_module)
    print(f"Module registration: {registration_success}")
    
    # Test module retrieval
    retrieved_module = screen_manager.get_module("test_module")
    print(f"Module retrieved: {retrieved_module is not None}")
    
    # Test getting all modules
    all_modules = screen_manager.get_all_modules()
    print(f"Total registered modules: {len(all_modules)}")
    
    # Test module status
    module_status = screen_manager.get_module_status("test_module")
    print(f"Module status: {module_status}")
    
    # Test navigation (would work in full Kivy app)
    print("Navigation test would require full Kivy app context")
    
    # Test unregistration
    unregister_success = screen_manager.unregister_module("test_module")
    print(f"Module unregistration: {unregister_success}")
    
    print("StosOSScreenManager tests completed successfully!")


def main():
    """Run all framework tests"""
    print("Starting StosOS Core Framework Tests")
    print("=" * 50)
    
    try:
        test_config_manager()
        test_error_handler()
        test_base_module()
        test_screen_manager()
        
        print("\n" + "=" * 50)
        print("All framework tests completed successfully!")
        print("Core framework is ready for module development.")
        
    except Exception as e:
        logger.error(f"Framework test failed: {e}")
        print(f"\nFramework test failed: {e}")
        return False
    
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)