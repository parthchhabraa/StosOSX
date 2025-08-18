"""
StosOS Theme Engine
Dark theme with color scheme and typography inspired by eDEX-UI
"""

from typing import Dict, Any, Tuple, Optional
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex


class StosOSTheme:
    """
    Central theme management for StosOS
    Provides dark theme with hacker-inspired aesthetics
    """
    
    # Color Palette - Dark theme with accent colors
    COLORS = {
        # Primary colors
        'background': get_color_from_hex('#0a0a0a'),      # Deep black
        'surface': get_color_from_hex('#1a1a1a'),        # Dark gray
        'surface_variant': get_color_from_hex('#2a2a2a'), # Medium gray
        
        # Text colors
        'text_primary': get_color_from_hex('#00ff41'),    # Matrix green
        'text_secondary': get_color_from_hex('#ffffff'),   # White
        'text_disabled': get_color_from_hex('#666666'),   # Gray
        'text_hint': get_color_from_hex('#888888'),       # Light gray
        
        # Accent colors
        'accent_primary': get_color_from_hex('#00ff41'),  # Matrix green
        'accent_secondary': get_color_from_hex('#ff6b35'), # Orange
        'accent_tertiary': get_color_from_hex('#00d4ff'), # Cyan
        
        # Status colors
        'success': get_color_from_hex('#00ff41'),         # Green
        'warning': get_color_from_hex('#ffaa00'),         # Orange
        'error': get_color_from_hex('#ff4444'),           # Red
        'info': get_color_from_hex('#00d4ff'),            # Cyan
        
        # Interactive states
        'hover': get_color_from_hex('#333333'),           # Light gray
        'pressed': get_color_from_hex('#444444'),         # Lighter gray
        'selected': get_color_from_hex('#00ff4120'),      # Green with alpha
        'disabled': get_color_from_hex('#1a1a1a'),        # Dark gray
        
        # Borders and dividers
        'border': get_color_from_hex('#333333'),          # Gray border
        'divider': get_color_from_hex('#222222'),         # Dark divider
        
        # Transparent overlays
        'overlay_light': get_color_from_hex('#ffffff10'),  # Light overlay
        'overlay_dark': get_color_from_hex('#00000080'),   # Dark overlay
    }
    
    # Typography - Use Kivy default fonts for compatibility
    FONTS = {
        'mono_regular': None,  # Use Kivy default
        'mono_bold': None,     # Use Kivy default
        'mono_light': None,    # Use Kivy default
        'system': None,        # Use Kivy default
    }
    
    # Font sizes
    FONT_SIZES = {
        'caption': sp(12),
        'body': sp(14),
        'body_large': sp(16),
        'title': sp(18),
        'title_large': sp(20),
        'headline': sp(24),
        'display': sp(32),
    }
    
    # Spacing and dimensions
    SPACING = {
        'xs': dp(4),
        'sm': dp(8),
        'md': dp(16),
        'lg': dp(24),
        'xl': dp(32),
        'xxl': dp(48),
    }
    
    # Component dimensions
    DIMENSIONS = {
        'button_height': dp(48),
        'input_height': dp(56),
        'panel_padding': dp(16),
        'border_radius': dp(8),
        'border_width': dp(1),
        'icon_size': dp(24),
        'icon_size_large': dp(32),
    }
    
    # Animation durations and easing
    ANIMATIONS = {
        'duration_fast': 0.15,
        'duration_normal': 0.25,
        'duration_slow': 0.4,
        'easing_standard': 'out_cubic',
        'easing_emphasized': 'out_quart',
        'easing_bounce': 'out_bounce',
    }
    
    @classmethod
    def get_color(cls, color_name: str) -> Tuple[float, float, float, float]:
        """
        Get color by name
        
        Args:
            color_name: Name of the color from COLORS dict
            
        Returns:
            RGBA color tuple
        """
        return cls.COLORS.get(color_name, cls.COLORS['text_primary'])
    
    @classmethod
    def get_font(cls, font_name: str) -> Optional[str]:
        """
        Get font by name with fallback to Kivy defaults
        
        Args:
            font_name: Name of the font from FONTS dict
            
        Returns:
            Font name string or None for Kivy default
        """
        return cls.FONTS.get(font_name, None)
    
    @classmethod
    def get_font_size(cls, size_name: str) -> float:
        """
        Get font size by name
        
        Args:
            size_name: Name of the size from FONT_SIZES dict
            
        Returns:
            Font size in sp
        """
        return cls.FONT_SIZES.get(size_name, cls.FONT_SIZES['body'])
    
    @classmethod
    def get_spacing(cls, spacing_name: str) -> float:
        """
        Get spacing by name
        
        Args:
            spacing_name: Name of the spacing from SPACING dict
            
        Returns:
            Spacing value in dp
        """
        return cls.SPACING.get(spacing_name, cls.SPACING['md'])
    
    @classmethod
    def get_dimension(cls, dimension_name: str) -> float:
        """
        Get dimension by name
        
        Args:
            dimension_name: Name of the dimension from DIMENSIONS dict
            
        Returns:
            Dimension value in dp
        """
        return cls.DIMENSIONS.get(dimension_name, dp(24))
    
    @classmethod
    def get_animation_config(cls, config_name: str) -> Any:
        """
        Get animation configuration by name
        
        Args:
            config_name: Name of the config from ANIMATIONS dict
            
        Returns:
            Animation configuration value
        """
        return cls.ANIMATIONS.get(config_name, cls.ANIMATIONS['duration_normal'])
    
    @classmethod
    def create_gradient_colors(cls, start_color: str, end_color: str, steps: int = 5) -> list:
        """
        Create gradient color steps between two colors
        
        Args:
            start_color: Starting color name
            end_color: Ending color name
            steps: Number of gradient steps
            
        Returns:
            List of RGBA color tuples
        """
        start = cls.get_color(start_color)
        end = cls.get_color(end_color)
        
        gradient = []
        for i in range(steps):
            ratio = i / (steps - 1) if steps > 1 else 0
            color = [
                start[j] + (end[j] - start[j]) * ratio
                for j in range(4)
            ]
            gradient.append(tuple(color))
        
        return gradient
    
    @classmethod
    def get_component_style(cls, component_type: str) -> Dict[str, Any]:
        """
        Get default style configuration for a component type
        
        Args:
            component_type: Type of component ('button', 'panel', 'input', etc.)
            
        Returns:
            Style configuration dictionary
        """
        styles = {
            'button': {
                'background_color': cls.get_color('surface_variant'),
                'color': cls.get_color('text_primary'),
                'font_size': cls.get_font_size('body'),
                'size_hint_y': None,
                'height': cls.get_dimension('button_height'),
                'padding': [cls.get_spacing('md'), cls.get_spacing('sm')],
            },
            'panel': {
                'background_color': cls.get_color('surface'),
                'padding': cls.get_dimension('panel_padding'),
                'spacing': cls.get_spacing('md'),
            },
            'input': {
                'background_color': cls.get_color('surface_variant'),
                'foreground_color': cls.get_color('text_secondary'),
                'font_size': cls.get_font_size('body'),
                'size_hint_y': None,
                'height': cls.get_dimension('input_height'),
                'padding': [cls.get_spacing('md'), cls.get_spacing('sm')],
            },
            'label': {
                'color': cls.get_color('text_secondary'),
                'font_size': cls.get_font_size('body'),
            },
            'title': {
                'color': cls.get_color('text_primary'),
                'font_size': cls.get_font_size('title_large'),
            },
        }
        
        return styles.get(component_type, {})