#!/usr/bin/env python3
"""
Basic setup test for StosOS
Verifies that core components can be imported and initialized
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that core modules can be imported"""
    try:
        # Test basic imports first (without Kivy dependencies)
        from core.config_manager import ConfigManager
        print("✓ ConfigManager import successful")
        
        # Test logger (without Kivy)
        from core.logger import StosOSLogger
        print("✓ Logger import successful")
        
        # Test base module (this imports Kivy, so it might fail without dependencies)
        try:
            from core.base_module import BaseModule
            print("✓ BaseModule import successful")
        except ImportError as e:
            print(f"⚠ BaseModule import failed (Kivy not installed): {e}")
            print("  This is expected if dependencies aren't installed yet")
        
        return True
    except ImportError as e:
        print(f"✗ Critical import failed: {e}")
        return False

def test_config_manager():
    """Test ConfigManager functionality"""
    try:
        from core.config_manager import ConfigManager
        config = ConfigManager()
        
        # Test getting default values
        app_name = config.get('app.name')
        assert app_name == 'StosOS X', f"Expected 'StosOS X', got '{app_name}'"
        
        # Test setting and getting values
        config.set('test.value', 'hello')
        test_value = config.get('test.value')
        assert test_value == 'hello', f"Expected 'hello', got '{test_value}'"
        
        print("✓ ConfigManager tests passed")
        return True
    except Exception as e:
        print(f"✗ ConfigManager test failed: {e}")
        return False

def test_logger():
    """Test logging functionality"""
    try:
        from core.logger import StosOSLogger
        logger_instance = StosOSLogger()
        logger = logger_instance.get_logger('test')
        logger.info("Test log message")
        print("✓ Logger test passed")
        return True
    except Exception as e:
        print(f"✗ Logger test failed: {e}")
        return False

def test_directory_structure():
    """Test that required directories exist"""
    required_dirs = ['core', 'modules', 'services', 'assets', 'config', 'logs', 'data']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            print(f"✗ Missing directory: {dir_name}")
            return False
    
    print("✓ Directory structure test passed")
    return True

if __name__ == '__main__':
    print("Running StosOS setup tests...\n")
    
    tests = [
        test_directory_structure,
        test_imports,
        test_config_manager,
        test_logger
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("✓ All tests passed! StosOS setup is ready.")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please check the setup.")
        sys.exit(1)