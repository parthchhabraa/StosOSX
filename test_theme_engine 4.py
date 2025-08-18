#!/usr/bin/env python3
"""
Test script for StosOS Theme Engine and UI Components
Verifies that all theme components work correctly
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_theme_engine():
    """Test the theme engine functionality"""
    print("Testing StosOS Theme Engine...")
    
    try:
        from ui.theme import StosOSTheme
        
        # Test color retrieval
        print("✓ Testing color system...")
        bg_color = StosOSTheme.get_color('background')
        assert len(bg_color) == 4, "Color should be RGBA tuple"
        assert all(0 <= c <= 1 for c in bg_color), "Color values should be 0-1"
        
        text_color = StosOSTheme.get_color('text_primary')
        assert text_color != bg_color, "Text and background should be different"
        
        # Test font system
        print("✓ Testing font system...")
        mono_font = StosOSTheme.get_font('mono_regular')
        assert mono_font is None or isinstance(mono_font, str), "Font should be string or None"
        
        body_size = StosOSTheme.get_font_size('body')
        assert isinstance(body_size, (int, float)), "Font size should be numeric"
        assert body_size > 0, "Font size should be positive"
        
        # Test spacing system
        print("✓ Testing spacing system...")
        md_spacing = StosOSTheme.get_spacing('md')
        assert isinstance(md_spacing, (int, float)), "Spacing should be numeric"
        assert md_spacing > 0, "Spacing should be positive"
        
        # Test component styles
        print("✓ Testing component styles...")
        button_style = StosOSTheme.get_component_style('button')
        assert isinstance(button_style, dict), "Style should be dictionary"
        assert 'background_color' in button_style, "Button style should have background_color"
        
        # Test gradient creation
        print("✓ Testing gradient creation...")
        gradient = StosOSTheme.create_gradient_colors('background', 'accent_primary', 3)
        assert len(gradient) == 3, "Gradient should have requested number of steps"
        assert all(len(color) == 4 for color in gradient), "All gradient colors should be RGBA"
        
        print("✅ Theme engine tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Theme engine test failed: {e}")
        return False

def test_animations():
    """Test the animation system"""
    print("\nTesting StosOS Animation System...")
    
    try:
        from ui.animations import StosOSAnimations, LoadingAnimations
        
        # Test easing functions
        print("✓ Testing easing functions...")
        ease_result = StosOSAnimations.ease_out_cubic(0.5)
        assert isinstance(ease_result, (int, float)), "Easing should return numeric value"
        assert 0 <= ease_result <= 1, "Easing result should be 0-1"
        
        bounce_result = StosOSAnimations.ease_out_bounce(0.5)
        assert isinstance(bounce_result, (int, float)), "Bounce easing should return numeric value"
        
        print("✅ Animation system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Animation system test failed: {e}")
        return False

def test_components():
    """Test UI components (basic instantiation)"""
    print("\nTesting StosOS UI Components...")
    
    try:
        # Import Kivy first to initialize
        import kivy
        kivy.require('2.0.0')
        
        from ui.components import (
            StosOSButton, StosOSLabel, StosOSTextInput, 
            StosOSPanel, StosOSCard
        )
        
        # Test basic component creation
        print("✓ Testing component instantiation...")
        
        # Button
        button = StosOSButton(text="Test Button")
        assert button.text == "Test Button", "Button text should be set"
        assert hasattr(button, 'button_type'), "Button should have button_type attribute"
        
        # Label (use system font to avoid font file issues)
        label = StosOSLabel(text="Test Label", font_name=None)
        assert label.text == "Test Label", "Label text should be set"
        assert hasattr(label, 'label_type'), "Label should have label_type attribute"
        
        # Text Input
        text_input = StosOSTextInput(placeholder="Test Input")
        assert text_input.hint_text == "Test Input", "TextInput placeholder should be set"
        
        # Panel
        panel = StosOSPanel(title="Test Panel")
        assert panel.title == "Test Panel", "Panel title should be set"
        
        # Card
        card = StosOSCard(title="Test Card")
        assert card.title == "Test Card", "Card title should be set"
        
        print("✅ UI components tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        return False

def test_ui_demo_module():
    """Test the UI demo module"""
    print("\nTesting UI Demo Module...")
    
    try:
        from modules.ui_demo import UIDemoModule
        
        # Create module instance
        demo_module = UIDemoModule()
        assert demo_module.module_id == "ui_demo", "Module ID should be set correctly"
        assert demo_module.display_name == "UI Demo", "Display name should be set correctly"
        
        # Test initialization
        init_result = demo_module.initialize()
        assert init_result == True, "Module should initialize successfully"
        assert demo_module._initialized == True, "Module should be marked as initialized"
        
        print("✅ UI Demo module tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ UI Demo module test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("StosOS Theme Engine & UI Components Test Suite")
    print("=" * 50)
    
    tests = [
        test_theme_engine,
        test_animations,
        test_components,
        test_ui_demo_module
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Theme engine is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())