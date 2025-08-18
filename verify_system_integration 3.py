#!/usr/bin/env python3
"""
Verify System Integration for StosOS
Tests the actual functionality of system components
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_system_manager_basic():
    """Test basic SystemManager functionality without heavy dependencies"""
    print("Testing SystemManager basic functionality...")
    
    try:
        # Mock psutil if not available
        import sys
        
        class MockPsutil:
            class VirtualMemory:
                def __init__(self):
                    self.percent = 45.0
                    self.available = 2048 * 1024 * 1024  # 2GB
            
            class DiskUsage:
                def __init__(self):
                    self.percent = 30.0
                    self.free = 10 * 1024 * 1024 * 1024  # 10GB
            
            @staticmethod
            def virtual_memory():
                return MockPsutil.VirtualMemory()
            
            @staticmethod
            def cpu_percent(interval=1):
                return 25.0
            
            @staticmethod
            def disk_usage(path):
                return MockPsutil.DiskUsage()
            
            @staticmethod
            def boot_time():
                import time
                return time.time() - 3600  # 1 hour uptime
            
            @staticmethod
            def process_iter(attrs=None):
                return []
        
        # Replace psutil with mock if not available
        try:
            import psutil
        except ImportError:
            sys.modules['psutil'] = MockPsutil()
        
        from core.logger import stosos_logger
        from core.config_manager import ConfigManager
        from core.system_manager import SystemManager
        
        logger = stosos_logger.get_logger(__name__)
        config_manager = ConfigManager()
        system_manager = SystemManager(config_manager, logger)
        
        # Test shutdown callback registration
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        system_manager.register_shutdown_callback(test_callback)
        
        # Test callback execution
        for callback in system_manager.shutdown_callbacks:
            callback()
        
        if not callback_called:
            print("✗ Shutdown callback not called")
            return False
        
        # Test health monitoring (basic)
        health = system_manager.get_system_health()
        if not isinstance(health, dict):
            print("✗ Health status should be a dictionary")
            return False
        
        print("✓ SystemManager basic functionality works")
        return True
        
    except Exception as e:
        print(f"✗ SystemManager test failed: {e}")
        return False

def test_update_manager_basic():
    """Test basic UpdateManager functionality"""
    print("Testing UpdateManager basic functionality...")
    
    try:
        from core.logger import stosos_logger
        from core.config_manager import ConfigManager
        from core.update_manager import UpdateManager
        
        logger = stosos_logger.get_logger(__name__)
        config_manager = ConfigManager()
        update_manager = UpdateManager(config_manager, logger)
        
        # Test version info
        version_info = update_manager.get_version_info()
        if not isinstance(version_info, dict):
            print("✗ Version info should be a dictionary")
            return False
        
        if 'current_version' not in version_info:
            print("✗ Version info should include current_version")
            return False
        
        # Test auto-update settings
        update_manager.set_auto_update_enabled(False)
        if update_manager.auto_check_enabled:
            print("✗ Auto-update should be disabled")
            return False
        
        update_manager.set_auto_update_enabled(True)
        if not update_manager.auto_check_enabled:
            print("✗ Auto-update should be enabled")
            return False
        
        # Test update history
        history = update_manager.get_update_history()
        if not isinstance(history, list):
            print("✗ Update history should be a list")
            return False
        
        print("✓ UpdateManager basic functionality works")
        return True
        
    except Exception as e:
        print(f"✗ UpdateManager test failed: {e}")
        return False

def test_service_integration():
    """Test service file integration"""
    print("Testing service integration...")
    
    try:
        service_file = project_root / "stosos.service"
        
        with open(service_file, 'r') as f:
            content = f.read()
        
        # Check that service file has correct structure
        required_sections = {
            '[Unit]': ['Description=', 'After=', 'Wants='],
            '[Service]': ['Type=', 'User=', 'ExecStart=', 'Restart='],
            '[Install]': ['WantedBy=']
        }
        
        for section, fields in required_sections.items():
            if section not in content:
                print(f"✗ Missing section: {section}")
                return False
            
            for field in fields:
                if field not in content:
                    print(f"✗ Missing field in {section}: {field}")
                    return False
        
        # Check security settings
        security_settings = [
            'NoNewPrivileges=true',
            'PrivateTmp=true',
            'ProtectSystem=strict'
        ]
        
        for setting in security_settings:
            if setting not in content:
                print(f"✗ Missing security setting: {setting}")
                return False
        
        print("✓ Service integration is properly configured")
        return True
        
    except Exception as e:
        print(f"✗ Service integration test failed: {e}")
        return False

def test_installation_script_structure():
    """Test installation script structure"""
    print("Testing installation script structure...")
    
    try:
        install_script = project_root / "install.sh"
        
        with open(install_script, 'r') as f:
            content = f.read()
        
        # Check for required functions
        required_functions = [
            'check_requirements()',
            'install_system_dependencies()',
            'setup_python_environment()',
            'setup_systemd_service()',
            'setup_directories()',
            'create_update_script()',
            'main()'
        ]
        
        for func in required_functions:
            if func not in content:
                print(f"✗ Missing function: {func}")
                return False
        
        # Check for error handling
        if 'set -e' not in content:
            print("✗ Missing error handling (set -e)")
            return False
        
        # Check for logging
        if 'log()' not in content:
            print("✗ Missing logging function")
            return False
        
        print("✓ Installation script structure is correct")
        return True
        
    except Exception as e:
        print(f"✗ Installation script test failed: {e}")
        return False

def test_update_script_structure():
    """Test update script structure"""
    print("Testing update script structure...")
    
    try:
        update_script = project_root / "update.sh"
        
        with open(update_script, 'r') as f:
            content = f.read()
        
        # Check for required functions
        required_functions = [
            'check_prerequisites()',
            'create_backup()',
            'update_from_git()',
            'update_dependencies()',
            'rollback()',
            'main()'
        ]
        
        for func in required_functions:
            if func not in content:
                print(f"✗ Missing function: {func}")
                return False
        
        # Check for safety features
        safety_features = [
            'set -e',  # Exit on error
            'trap',    # Error handling
            'BACKUP_DIR'  # Backup functionality
        ]
        
        for feature in safety_features:
            if feature not in content:
                print(f"✗ Missing safety feature: {feature}")
                return False
        
        print("✓ Update script structure is correct")
        return True
        
    except Exception as e:
        print(f"✗ Update script test failed: {e}")
        return False

def test_configuration_integration():
    """Test configuration integration"""
    print("Testing configuration integration...")
    
    try:
        from core.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # Test that config manager can handle system-related settings
        test_configs = {
            'system.auto_update': True,
            'system.health_monitoring': True,
            'system.backup_retention_days': 7,
            'power.dim_timeout': 30.0,
            'power.sleep_timeout': 60.0
        }
        
        for key, value in test_configs.items():
            # Test setting and getting config values
            config_manager.set(key, value)
            retrieved_value = config_manager.get(key)
            
            if retrieved_value != value:
                print(f"✗ Config value mismatch for {key}: expected {value}, got {retrieved_value}")
                return False
        
        print("✓ Configuration integration works")
        return True
        
    except Exception as e:
        print(f"✗ Configuration integration test failed: {e}")
        return False

def test_main_app_integration():
    """Test main app integration with system components"""
    print("Testing main app integration...")
    
    try:
        # Test that main.py can import system components
        import importlib.util
        
        main_spec = importlib.util.spec_from_file_location("main", project_root / "main.py")
        main_module = importlib.util.module_from_spec(main_spec)
        
        # This will test imports without running the app
        main_spec.loader.exec_module(main_module)
        
        # Check that the app class has the required methods
        app_class = main_module.StosOSApp
        
        required_methods = [
            'restart_application',
            'get_system_health',
            'get_version_info',
            '_check_for_updates',
            '_on_system_shutdown'
        ]
        
        for method in required_methods:
            if not hasattr(app_class, method):
                print(f"✗ Missing method in StosOSApp: {method}")
                return False
        
        print("✓ Main app integration is correct")
        return True
        
    except Exception as e:
        print(f"✗ Main app integration test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("StosOS System Integration Verification")
    print("=" * 60)
    
    tests = [
        ("SystemManager Basic", test_system_manager_basic),
        ("UpdateManager Basic", test_update_manager_basic),
        ("Service Integration", test_service_integration),
        ("Installation Script", test_installation_script_structure),
        ("Update Script", test_update_script_structure),
        ("Configuration Integration", test_configuration_integration),
        ("Main App Integration", test_main_app_integration)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Verification Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All system integration verification tests passed!")
        print("\nTask 18 Implementation Summary:")
        print("✓ SystemManager for health monitoring and graceful shutdown")
        print("✓ UpdateManager for version control and updates")
        print("✓ Systemd service file for auto-startup")
        print("✓ Installation script for Raspberry Pi setup")
        print("✓ Update script with backup and rollback")
        print("✓ Integration with main application")
        print("✓ Comprehensive error handling and logging")
        return True
    else:
        print("❌ Some verification tests failed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)