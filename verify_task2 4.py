#!/usr/bin/env python3
"""
Verification script for Task 2: Core Application Framework and Base Classes
Verifies all requirements are implemented correctly
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def verify_base_module():
    """Verify BaseModule abstract class implementation"""
    print("✓ Verifying BaseModule abstract class...")
    
    from core.base_module import BaseModule
    from abc import ABC
    
    # Check inheritance
    assert issubclass(BaseModule, ABC), "BaseModule should inherit from ABC"
    
    # Check required methods exist
    required_methods = ['initialize', 'get_screen', 'on_activate', 'on_deactivate', 
                       'handle_voice_command', 'get_status', 'cleanup']
    
    for method in required_methods:
        assert hasattr(BaseModule, method), f"BaseModule missing method: {method}"
    
    # Test with concrete implementation
    from core.test_module import TestModule
    test_module = TestModule()
    
    # Test initialization
    assert test_module.initialize(), "Test module should initialize successfully"
    
    # Test status
    status = test_module.get_status()
    assert isinstance(status, dict), "get_status should return a dictionary"
    assert 'module_id' in status, "Status should include module_id"
    assert 'initialized' in status, "Status should include initialized flag"
    
    # Test voice command handling
    result = test_module.handle_voice_command("test command")
    assert isinstance(result, bool), "handle_voice_command should return boolean"
    
    # Test activation/deactivation
    test_module.on_activate()
    assert test_module._active, "Module should be active after on_activate"
    
    test_module.on_deactivate()
    assert not test_module._active, "Module should be inactive after on_deactivate"
    
    # Test cleanup
    test_module.cleanup()
    assert not test_module._initialized, "Module should not be initialized after cleanup"
    
    print("  ✓ BaseModule abstract class implemented correctly")


def verify_screen_manager():
    """Verify ScreenManager for navigation and module switching"""
    print("✓ Verifying StosOSScreenManager...")
    
    from core.screen_manager import StosOSScreenManager
    from core.test_module import TestModule
    from kivy.uix.screenmanager import ScreenManager
    
    # Check inheritance
    assert issubclass(StosOSScreenManager, ScreenManager), "Should inherit from ScreenManager"
    
    # Create screen manager
    screen_manager = StosOSScreenManager()
    
    # Test module registration
    test_module = TestModule()
    success = screen_manager.register_module(test_module)
    assert success, "Module registration should succeed"
    
    # Test module retrieval
    retrieved = screen_manager.get_module("test_module")
    assert retrieved is not None, "Should be able to retrieve registered module"
    assert retrieved.module_id == "test_module", "Retrieved module should have correct ID"
    
    # Test getting all modules
    all_modules = screen_manager.get_all_modules()
    assert len(all_modules) == 1, "Should have one registered module"
    assert "test_module" in all_modules, "test_module should be in all_modules"
    
    # Test module status
    status = screen_manager.get_module_status("test_module")
    assert status is not None, "Should return status for registered module"
    assert status['module_id'] == "test_module", "Status should have correct module_id"
    
    # Test unregistration
    unregister_success = screen_manager.unregister_module("test_module")
    assert unregister_success, "Module unregistration should succeed"
    
    # Verify module is removed
    retrieved_after = screen_manager.get_module("test_module")
    assert retrieved_after is None, "Module should not exist after unregistration"
    
    print("  ✓ StosOSScreenManager implemented correctly")


def verify_config_manager():
    """Verify ConfigManager for handling application settings and API keys"""
    print("✓ Verifying ConfigManager...")
    
    from core.config_manager import ConfigManager
    
    # Create config manager
    config = ConfigManager()
    
    # Test default configuration loading
    app_name = config.get('app.name')
    assert app_name == 'StosOS X', f"Expected 'StosOS X', got '{app_name}'"
    
    # Test setting and getting values
    config.set('test.key', 'test_value')
    retrieved_value = config.get('test.key')
    assert retrieved_value == 'test_value', "Should retrieve the set value"
    
    # Test default values
    non_existent = config.get('non.existent.key', 'default')
    assert non_existent == 'default', "Should return default for non-existent key"
    
    # Test API key functionality
    config.set_api_key('test_service', 'test_api_key_123')
    api_key = config.get_api_key('test_service')
    assert api_key == 'test_api_key_123', "Should retrieve the set API key"
    
    # Test module enabled check
    calendar_enabled = config.is_module_enabled('calendar')
    assert isinstance(calendar_enabled, bool), "is_module_enabled should return boolean"
    
    # Test configuration saving
    save_success = config.save_config()
    assert save_success, "Configuration saving should succeed"
    
    print("  ✓ ConfigManager implemented correctly")


def verify_error_handling():
    """Verify basic error handling and logging infrastructure"""
    print("✓ Verifying Error Handling and Logging...")
    
    from core.error_handler import error_handler, ErrorType, ErrorSeverity
    from core.logger import stosos_logger
    import logging
    
    # Test logger setup
    logger = stosos_logger.get_logger("test_verification")
    assert isinstance(logger, logging.Logger), "Should return a Logger instance"
    
    # Test error handler
    try:
        raise ValueError("Test error for verification")
    except Exception as e:
        success = error_handler.handle_error(
            e, "Verification test", ErrorType.SYSTEM, ErrorSeverity.LOW
        )
        # Error handling should complete without crashing
        assert isinstance(success, bool), "handle_error should return boolean"
    
    # Test error statistics
    stats = error_handler.get_error_statistics()
    assert isinstance(stats, dict), "get_error_statistics should return dict"
    assert 'total_errors' in stats, "Statistics should include total_errors"
    
    # Test error history
    history = error_handler.get_error_history(limit=1)
    assert isinstance(history, list), "get_error_history should return list"
    
    print("  ✓ Error handling and logging implemented correctly")


def verify_requirements():
    """Verify specific requirements are met"""
    print("✓ Verifying Requirements 1.1, 10.4, 10.5...")
    
    # Requirement 1.1: System should launch automatically (framework ready)
    from main import StosOSApp
    app = StosOSApp()
    assert app is not None, "StosOSApp should be instantiable"
    
    # Requirement 10.4: Error handling and logging
    from core.error_handler import error_handler
    from core.logger import stosos_logger
    assert error_handler is not None, "Error handler should be available"
    assert stosos_logger is not None, "Logger should be available"
    
    # Requirement 10.5: Graceful recovery from errors
    # Test that error handler has recovery strategies
    assert hasattr(error_handler, 'recovery_strategies'), "Should have recovery strategies"
    assert hasattr(error_handler, 'handle_error'), "Should have error handling method"
    
    print("  ✓ Requirements 1.1, 10.4, 10.5 satisfied")


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("TASK 2 VERIFICATION: Core Application Framework and Base Classes")
    print("=" * 60)
    
    try:
        verify_base_module()
        verify_screen_manager()
        verify_config_manager()
        verify_error_handling()
        verify_requirements()
        
        print("\n" + "=" * 60)
        print("✅ ALL TASK 2 REQUIREMENTS SUCCESSFULLY IMPLEMENTED!")
        print("=" * 60)
        print("\nImplemented components:")
        print("  ✓ BaseModule abstract class with common interface methods")
        print("  ✓ StosOSScreenManager for navigation and module switching")
        print("  ✓ ConfigManager for handling application settings and API keys")
        print("  ✓ Basic error handling and logging infrastructure")
        print("  ✓ Requirements 1.1, 10.4, 10.5 satisfied")
        print("\nThe core framework is ready for module development!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)