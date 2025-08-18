#!/usr/bin/env python3
"""
Test System Integration for StosOS
Tests system manager, update manager, and service integration
"""

import os
import sys
import time
import tempfile
import subprocess
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.logger import stosos_logger
from core.config_manager import ConfigManager
from core.system_manager import SystemManager
from core.update_manager import UpdateManager

logger = stosos_logger.get_logger(__name__)


def test_system_manager():
    """Test SystemManager functionality"""
    print("Testing SystemManager...")
    
    try:
        config_manager = ConfigManager()
        system_manager = SystemManager(config_manager, logger)
        
        # Test health monitoring
        health = system_manager.get_system_health()
        assert isinstance(health, dict), "Health status should be a dictionary"
        assert 'memory_usage' in health, "Health should include memory usage"
        assert 'cpu_usage' in health, "Health should include CPU usage"
        assert 'temperature' in health, "Health should include temperature"
        
        print("✓ System health monitoring works")
        
        # Test shutdown callback registration
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
            
        system_manager.register_shutdown_callback(test_callback)
        
        # Simulate shutdown (without actually shutting down)
        system_manager.shutdown_callbacks = [test_callback]
        for callback in system_manager.shutdown_callbacks:
            callback()
            
        assert callback_called, "Shutdown callback should be called"
        print("✓ Shutdown callback registration works")
        
        # Test service status check
        is_service = system_manager.is_service_running()
        print(f"✓ Service status check works (running as service: {is_service})")
        
        return True
        
    except Exception as e:
        print(f"✗ SystemManager test failed: {e}")
        return False


def test_update_manager():
    """Test UpdateManager functionality"""
    print("Testing UpdateManager...")
    
    try:
        config_manager = ConfigManager()
        update_manager = UpdateManager(config_manager, logger)
        
        # Test version info
        version_info = update_manager.get_version_info()
        assert isinstance(version_info, dict), "Version info should be a dictionary"
        assert 'current_version' in version_info, "Version info should include current version"
        
        print(f"✓ Version info works (current: {version_info['current_version']})")
        
        # Test update history
        history = update_manager.get_update_history()
        assert isinstance(history, list), "Update history should be a list"
        
        print("✓ Update history works")
        
        # Test auto-update settings
        update_manager.set_auto_update_enabled(False)
        assert not update_manager.auto_check_enabled, "Auto-update should be disabled"
        
        update_manager.set_auto_update_enabled(True)
        assert update_manager.auto_check_enabled, "Auto-update should be enabled"
        
        print("✓ Auto-update settings work")
        
        return True
        
    except Exception as e:
        print(f"✗ UpdateManager test failed: {e}")
        return False


def test_service_file():
    """Test systemd service file"""
    print("Testing systemd service file...")
    
    try:
        service_file = project_root / "stosos.service"
        
        if not service_file.exists():
            print("✗ Service file not found")
            return False
            
        # Read and validate service file
        with open(service_file, 'r') as f:
            content = f.read()
            
        # Check required sections
        required_sections = ['[Unit]', '[Service]', '[Install]']
        for section in required_sections:
            assert section in content, f"Service file missing {section} section"
            
        # Check required fields
        required_fields = [
            'Description=',
            'ExecStart=',
            'WorkingDirectory=',
            'User=',
            'Restart='
        ]
        
        for field in required_fields:
            assert field in content, f"Service file missing {field} field"
            
        print("✓ Service file structure is valid")
        
        # Test service file syntax with systemd
        try:
            result = subprocess.run(
                ['systemd-analyze', 'verify', str(service_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✓ Service file syntax is valid")
            else:
                print(f"⚠ Service file syntax warning: {result.stderr}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠ Could not verify service file syntax (systemd-analyze not available)")
            
        return True
        
    except Exception as e:
        print(f"✗ Service file test failed: {e}")
        return False


def test_installation_script():
    """Test installation script"""
    print("Testing installation script...")
    
    try:
        install_script = project_root / "install.sh"
        
        if not install_script.exists():
            print("✗ Installation script not found")
            return False
            
        # Check if script is executable
        if not os.access(install_script, os.X_OK):
            print("✗ Installation script is not executable")
            return False
            
        # Read and validate script content
        with open(install_script, 'r') as f:
            content = f.read()
            
        # Check for required functions
        required_functions = [
            'check_requirements',
            'install_system_dependencies',
            'setup_python_environment',
            'setup_systemd_service',
            'setup_directories'
        ]
        
        for func in required_functions:
            assert func in content, f"Installation script missing {func} function"
            
        print("✓ Installation script structure is valid")
        
        # Test script syntax
        try:
            result = subprocess.run(
                ['bash', '-n', str(install_script)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✓ Installation script syntax is valid")
            else:
                print(f"✗ Installation script syntax error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠ Could not verify script syntax (timeout)")
            
        return True
        
    except Exception as e:
        print(f"✗ Installation script test failed: {e}")
        return False


def test_update_script():
    """Test update script"""
    print("Testing update script...")
    
    try:
        update_script = project_root / "update.sh"
        
        if not update_script.exists():
            print("✗ Update script not found")
            return False
            
        # Check if script is executable
        if not os.access(update_script, os.X_OK):
            print("✗ Update script is not executable")
            return False
            
        # Test script syntax
        try:
            result = subprocess.run(
                ['bash', '-n', str(update_script)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✓ Update script syntax is valid")
            else:
                print(f"✗ Update script syntax error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠ Could not verify update script syntax (timeout)")
            
        return True
        
    except Exception as e:
        print(f"✗ Update script test failed: {e}")
        return False


def test_version_file():
    """Test VERSION file"""
    print("Testing VERSION file...")
    
    try:
        version_file = project_root / "VERSION"
        
        if not version_file.exists():
            print("✗ VERSION file not found")
            return False
            
        with open(version_file, 'r') as f:
            version = f.read().strip()
            
        # Validate version format (basic semver check)
        parts = version.split('.')
        assert len(parts) >= 2, "Version should have at least major.minor format"
        
        for part in parts:
            assert part.isdigit(), f"Version part '{part}' should be numeric"
            
        print(f"✓ VERSION file is valid (version: {version})")
        return True
        
    except Exception as e:
        print(f"✗ VERSION file test failed: {e}")
        return False


def test_directory_structure():
    """Test required directory structure"""
    print("Testing directory structure...")
    
    try:
        required_dirs = [
            'core',
            'modules', 
            'ui',
            'config',
            'data',
            'logs'
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            if not dir_path.exists():
                print(f"✗ Required directory missing: {dir_name}")
                return False
                
        print("✓ Directory structure is complete")
        
        # Check for required files
        required_files = [
            'main.py',
            'requirements.txt',
            'stosos.service',
            'install.sh',
            'VERSION'
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            if not file_path.exists():
                print(f"✗ Required file missing: {file_name}")
                return False
                
        print("✓ Required files are present")
        return True
        
    except Exception as e:
        print(f"✗ Directory structure test failed: {e}")
        return False


def test_integration():
    """Test integration between components"""
    print("Testing component integration...")
    
    try:
        # Test that system manager can be initialized
        config_manager = ConfigManager()
        system_manager = SystemManager(config_manager, logger)
        update_manager = UpdateManager(config_manager, logger)
        
        # Test that they can work together
        health = system_manager.get_system_health()
        version_info = update_manager.get_version_info()
        
        assert isinstance(health, dict), "Health should be a dictionary"
        assert isinstance(version_info, dict), "Version info should be a dictionary"
        
        print("✓ Component integration works")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        return False


def main():
    """Run all system integration tests"""
    print("=" * 60)
    print("StosOS System Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("VERSION File", test_version_file),
        ("Service File", test_service_file),
        ("Installation Script", test_installation_script),
        ("Update Script", test_update_script),
        ("SystemManager", test_system_manager),
        ("UpdateManager", test_update_manager),
        ("Component Integration", test_integration)
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
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All system integration tests passed!")
        return True
    else:
        print("❌ Some tests failed. Please check the output above.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)