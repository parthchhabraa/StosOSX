#!/usr/bin/env python3
"""
Simple System Integration Test for StosOS
Tests basic functionality without heavy dependencies
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_file_structure():
    """Test that all required files exist"""
    print("Testing file structure...")
    
    required_files = [
        'main.py',
        'stosos.service',
        'install.sh',
        'update.sh',
        'VERSION',
        'core/system_manager.py',
        'core/update_manager.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        full_path = project_root / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    print("✓ All required files exist")
    return True

def test_service_file():
    """Test systemd service file content"""
    print("Testing service file...")
    
    service_file = project_root / "stosos.service"
    
    try:
        with open(service_file, 'r') as f:
            content = f.read()
        
        required_sections = ['[Unit]', '[Service]', '[Install]']
        for section in required_sections:
            if section not in content:
                print(f"✗ Missing section: {section}")
                return False
        
        required_fields = [
            'Description=StosOS Desktop Environment',
            'ExecStart=',
            'WorkingDirectory=',
            'User=pi',
            'Restart=always'
        ]
        
        for field in required_fields:
            if field not in content:
                print(f"✗ Missing field: {field}")
                return False
        
        print("✓ Service file is valid")
        return True
        
    except Exception as e:
        print(f"✗ Service file test failed: {e}")
        return False

def test_version_file():
    """Test VERSION file"""
    print("Testing VERSION file...")
    
    try:
        version_file = project_root / "VERSION"
        
        with open(version_file, 'r') as f:
            version = f.read().strip()
        
        # Basic version validation
        if not version:
            print("✗ VERSION file is empty")
            return False
        
        parts = version.split('.')
        if len(parts) < 2:
            print("✗ Invalid version format")
            return False
        
        print(f"✓ VERSION file is valid (version: {version})")
        return True
        
    except Exception as e:
        print(f"✗ VERSION file test failed: {e}")
        return False

def test_scripts_executable():
    """Test that scripts are executable"""
    print("Testing script permissions...")
    
    scripts = ['install.sh', 'update.sh']
    
    for script in scripts:
        script_path = project_root / script
        if not os.access(script_path, os.X_OK):
            print(f"✗ Script not executable: {script}")
            return False
    
    print("✓ All scripts are executable")
    return True

def test_python_syntax():
    """Test Python files for syntax errors"""
    print("Testing Python syntax...")
    
    python_files = [
        'core/system_manager.py',
        'core/update_manager.py'
    ]
    
    for py_file in python_files:
        file_path = project_root / py_file
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Try to compile the code
            compile(content, str(file_path), 'exec')
            
        except SyntaxError as e:
            print(f"✗ Syntax error in {py_file}: {e}")
            return False
        except Exception as e:
            print(f"✗ Error checking {py_file}: {e}")
            return False
    
    print("✓ Python syntax is valid")
    return True

def main():
    """Run basic system tests"""
    print("=" * 50)
    print("StosOS System Basic Tests")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Service File", test_service_file),
        ("VERSION File", test_version_file),
        ("Script Permissions", test_scripts_executable),
        ("Python Syntax", test_python_syntax)
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
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("🎉 All basic tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)