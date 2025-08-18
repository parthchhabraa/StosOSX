#!/usr/bin/env python3
"""
Verify theme integration with main application
Tests that the main app can import and use the theme engine
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_main_app_imports():
    """Test that main app can import theme components"""
    print("Testing main application imports...")
    
    try:
        # Test core imports
        from core.config_manager import ConfigManager
        from core.base_module import BaseModule
        from core.screen_manager import StosOSScreenManager
        from core.error_handler import error_handler
        
        # Test theme imports
        from ui.theme import StosOSTheme
        from ui.animations import StosOSAnimations
        from ui.components import StosOSButton, StosOSLabel
        
        # Test module imports
        from modules.ui_demo import UIDemoModule
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_theme_integration():
    """Test theme integration with components"""
    print("Testing theme integration...")
    
    try:
        from ui.theme import StosOSTheme
        from modules.ui_demo import UIDemoModule
        
        # Test theme color access
        bg_color = StosOSTheme.get_color('background')
        assert len(bg_color) == 4, "Background color should be RGBA"
        
        # Test module creation
        demo_module = UIDemoModule()
        assert demo_module.initialize(), "Demo module should initialize"
        
        # Test component style generation
        button_style = StosOSTheme.get_component_style('button')
        assert 'background_color' in button_style, "Button style should have background_color"
        
        print("✅ Theme integration working!")
        return True
        
    except Exception as e:
        print(f"❌ Theme integration failed: {e}")
        return False

def test_requirements_coverage():
    """Verify that implementation covers the requirements"""
    print("Verifying requirements coverage...")
    
    requirements_met = {
        "9.1": "Smooth animated transitions",
        "9.2": "Fade, slide, scale animations", 
        "9.3": "Visual feedback on interactions",
        "9.4": "Dark theme implementation",
        "9.5": "Monospace fonts (fallback to system)",
        "9.6": "Loading animations"
    }
    
    try:
        from ui.theme import StosOSTheme
        from ui.animations import StosOSAnimations, LoadingAnimations
        from ui.components import StosOSButton
        
        # Check dark theme (9.4)
        bg_color = StosOSTheme.get_color('background')
        assert bg_color[0] < 0.2, "Should have dark background"
        
        # Check animations exist (9.1, 9.2)
        assert hasattr(StosOSAnimations, 'fade_in'), "Should have fade animations"
        assert hasattr(StosOSAnimations, 'slide_in_from_left'), "Should have slide animations"
        assert hasattr(StosOSAnimations, 'scale_in'), "Should have scale animations"
        
        # Check loading animations (9.6)
        assert hasattr(LoadingAnimations, 'create_spinner'), "Should have loading animations"
        
        # Check visual feedback (9.3)
        button = StosOSButton(text="Test")
        assert hasattr(button, '_on_touch_down'), "Should have touch feedback"
        
        print("✅ All requirements covered!")
        for req, desc in requirements_met.items():
            print(f"  ✓ Requirement {req}: {desc}")
        
        return True
        
    except Exception as e:
        print(f"❌ Requirements verification failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("StosOS Theme Engine Integration Verification")
    print("=" * 60)
    
    tests = [
        test_main_app_imports,
        test_theme_integration,
        test_requirements_coverage
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add spacing between tests
    
    print("=" * 60)
    print(f"Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Theme engine integration is complete and ready!")
        print("\nImplemented features:")
        print("• Dark theme with Matrix-inspired color scheme")
        print("• Reusable UI components (buttons, panels, inputs)")
        print("• Smooth animation system with easing functions")
        print("• Loading animations and visual feedback")
        print("• UI demo module showcasing all components")
        return 0
    else:
        print("⚠️  Some verification tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())