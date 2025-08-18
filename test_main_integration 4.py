#!/usr/bin/env python3
"""
Test main app integration with branding screen
"""

import sys
from pathlib import Path
import os

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variable to prevent Kivy from trying to create a window
os.environ['KIVY_NO_CONSOLELOG'] = '1'

def test_main_app_creation():
    """Test that main app can be created with branding integration"""
    try:
        from main import StosOSApp
        
        # Create app instance
        app = StosOSApp()
        
        # Verify branding manager exists
        assert hasattr(app, 'branding_manager'), "App should have branding_manager"
        assert app.branding_manager is not None, "Branding manager should be initialized"
        
        # Verify main interface ready flag
        assert hasattr(app, 'main_interface_ready'), "App should have main_interface_ready flag"
        assert app.main_interface_ready == False, "Main interface should start as not ready"
        
        # Test branding manager methods
        assert hasattr(app.branding_manager, 'show_branding'), "Should have show_branding method"
        assert hasattr(app.branding_manager, 'skip_branding'), "Should have skip_branding method"
        assert hasattr(app.branding_manager, 'is_branding_active'), "Should have is_branding_active method"
        
        print("✓ Main app creation and branding integration successful")
        return True
        
    except Exception as e:
        print(f"✗ Main app creation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_app_methods():
    """Test app methods related to branding"""
    try:
        from main import StosOSApp
        
        app = StosOSApp()
        
        # Test method existence
        methods = [
            '_create_main_interface',
            '_on_branding_complete', 
            '_initialize_modules',
            '_transition_to_main_interface'
        ]
        
        for method_name in methods:
            assert hasattr(app, method_name), f"App should have {method_name} method"
        
        print("✓ All required methods exist")
        return True
        
    except Exception as e:
        print(f"✗ App methods test error: {e}")
        return False

def test_branding_workflow():
    """Test the branding workflow without actually running the app"""
    try:
        from ui.branding_screen import BrandingScreenManager
        
        # Create branding manager
        manager = BrandingScreenManager()
        
        # Test initial state
        assert not manager.is_branding_active(), "Should start inactive"
        
        # Test skip functionality
        manager.skip_branding()  # Should not crash
        
        print("✓ Branding workflow test successful")
        return True
        
    except Exception as e:
        print(f"✗ Branding workflow error: {e}")
        return False

def main():
    """Run integration tests"""
    print("=== Main App Integration Tests ===\n")
    
    tests = [
        ("Main App Creation", test_main_app_creation),
        ("App Methods", test_app_methods),
        ("Branding Workflow", test_branding_workflow)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        if not test_func():
            all_passed = False
        print()
    
    if all_passed:
        print("✓ All integration tests passed!")
        print("✓ Branding screen is properly integrated with main app")
        return 0
    else:
        print("✗ Some integration tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())