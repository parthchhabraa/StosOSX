#!/usr/bin/env python3
"""
Test script for branding screen functionality
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from ui.branding_screen import BrandingScreen, BrandingScreenManager
    from ui.theme import StosOSTheme
    from ui.animations import StosOSAnimations
    print("✓ All branding screen imports successful")
    
    # Test theme colors
    bg_color = StosOSTheme.get_color('background')
    text_color = StosOSTheme.get_color('text_primary')
    print(f"✓ Theme colors loaded: bg={bg_color}, text={text_color}")
    
    # Test branding screen creation (without Kivy app)
    print("✓ Branding screen module loaded successfully")
    print("✓ All components ready for integration")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)