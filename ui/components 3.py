"""
StosOS Reusable UI Components
Consistent styled components with dark theme
"""

from typing import Optional, Callable, Any, Union
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.clock import Clock

from .theme import StosOSTheme
from .animations import StosOSAnimations


class StosOSButton(Button):
    """
    Styled button component with hover effects and animations
    """
    
    def __init__(self, text: str = "", button_type: str = "primary", 
                 icon: str = "", on_press_callback: Optional[Callable] = None, **kwargs):
        # Apply theme styles
        style = StosOSTheme.get_component_style('button')
        
        # Button type variations
        if button_type == "secondary":
            style['background_color'] = StosOSTheme.get_color('surface')
            style['color'] = StosOSTheme.get_color('text_secondary')
        elif button_type == "accent":
            style['background_color'] = StosOSTheme.get_color('accent_primary')
            style['color'] = StosOSTheme.get_color('background')
        elif button_type == "danger":
            style['background_color'] = StosOSTheme.get_color('error')
            style['color'] = StosOSTheme.get_color('text_secondary')
        
        # Merge with kwargs
        for key, value in style.items():
            if key not in kwargs:
                kwargs[key] = value
        
        # Handle font gracefully
        if 'font_name' in kwargs:
            try:
                super().__init__(text=text, **kwargs)
            except Exception:
                # Fallback to no custom font
                kwargs.pop('font_name', None)
                super().__init__(text=text, **kwargs)
        else:
            super().__init__(text=text, **kwargs)
        
        self.button_type = button_type
        self.icon = icon
        self.original_color = self.background_color[:]
        self.hover_color = StosOSTheme.get_color('hover')
        self.pressed_color = StosOSTheme.get_color('pressed')
        
        # Store callback
        if on_press_callback:
            self.bind(on_press=lambda x: on_press_callback())
        
        # Bind events for hover effects
        self.bind(on_touch_down=self._on_touch_down)
        self.bind(on_touch_up=self._on_touch_up)
        
        # Add visual feedback
        self._setup_graphics()
    
    def _setup_graphics(self):
        """Setup custom graphics for the button"""
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[StosOSTheme.get_dimension('border_radius')]
            )
        
        # Update graphics when size/pos changes
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        """Update graphics when widget changes"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
    
    def _on_touch_down(self, touch):
        """Handle touch down for press effect"""
        if self.collide_point(*touch.pos):
            # Animate to pressed state
            StosOSAnimations.glow_effect(self, duration=0.1)
            return True
        return False
    
    def _on_touch_up(self, touch):
        """Handle touch up to reset state"""
        if self.collide_point(*touch.pos):
            # Quick pulse effect
            StosOSAnimations.pulse(self, scale=1.05, duration=0.2)
        return False


class StosOSLabel(Label):
    """
    Styled label component with theme typography
    """
    
    def __init__(self, text: str = "", label_type: str = "body", **kwargs):
        # Apply theme styles based on type
        if label_type == "title":
            style = StosOSTheme.get_component_style('title')
        else:
            style = StosOSTheme.get_component_style('label')
        
        # Merge with kwargs
        for key, value in style.items():
            if key not in kwargs:
                kwargs[key] = value
        
        # Handle font gracefully
        if 'font_name' in kwargs:
            try:
                super().__init__(text=text, **kwargs)
            except Exception:
                # Fallback to no custom font
                kwargs.pop('font_name', None)
                super().__init__(text=text, **kwargs)
        else:
            super().__init__(text=text, **kwargs)
        self.label_type = label_type
    
    def animate_text_change(self, new_text: str, duration: float = 0.3):
        """Animate text change with fade effect"""
        def set_new_text():
            self.text = new_text
            StosOSAnimations.fade_in(self, duration=duration/2)
        
        StosOSAnimations.fade_out(self, duration=duration/2, callback=set_new_text)


class StosOSTextInput(TextInput):
    """
    Styled text input component with focus effects
    """
    
    def __init__(self, placeholder: str = "", input_type: str = "text", **kwargs):
        # Apply theme styles
        style = StosOSTheme.get_component_style('input')
        
        # Merge with kwargs
        for key, value in style.items():
            if key not in kwargs:
                kwargs[key] = value
        
        super().__init__(**kwargs)
        
        self.placeholder = placeholder
        self.input_type = input_type
        self.hint_text = placeholder
        
        # Focus effects
        self.bind(focus=self._on_focus_change)
        
        # Setup graphics
        self._setup_graphics()
    
    def _setup_graphics(self):
        """Setup custom graphics for the input"""
        with self.canvas.before:
            Color(*StosOSTheme.get_color('border'))
            self.border_line = Line(
                rectangle=(self.x, self.y, self.width, self.height),
                width=StosOSTheme.get_dimension('border_width')
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        """Update graphics when widget changes"""
        if hasattr(self, 'border_line'):
            self.border_line.rectangle = (self.x, self.y, self.width, self.height)
    
    def _on_focus_change(self, instance, focused):
        """Handle focus change effects"""
        if focused:
            # Glow effect on focus
            StosOSAnimations.glow_effect(self, duration=0.2)
        else:
            # Fade back to normal
            pass


class StosOSPanel(BoxLayout):
    """
    Styled panel component with background and padding
    """
    
    def __init__(self, title: str = "", panel_type: str = "default", **kwargs):
        # Apply theme styles
        style = StosOSTheme.get_component_style('panel')
        
        # Panel type variations
        if panel_type == "elevated":
            style['background_color'] = StosOSTheme.get_color('surface_variant')
        elif panel_type == "outlined":
            style['background_color'] = StosOSTheme.get_color('background')
        
        # Set default orientation
        if 'orientation' not in kwargs:
            kwargs['orientation'] = 'vertical'
        
        super().__init__(**kwargs)
        
        self.title = title
        self.panel_type = panel_type
        self.background_color = style.get('background_color', StosOSTheme.get_color('surface'))
        
        # Setup graphics
        self._setup_graphics()
        
        # Add title if provided
        if title:
            self._add_title()
    
    def _setup_graphics(self):
        """Setup panel background"""
        with self.canvas.before:
            Color(*self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[StosOSTheme.get_dimension('border_radius')]
            )
            
            # Add border for outlined panels
            if self.panel_type == "outlined":
                Color(*StosOSTheme.get_color('border'))
                self.border_line = Line(
                    rounded_rectangle=(
                        self.x, self.y, self.width, self.height,
                        StosOSTheme.get_dimension('border_radius')
                    ),
                    width=StosOSTheme.get_dimension('border_width')
                )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        """Update graphics when widget changes"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
        
        if hasattr(self, 'border_line'):
            self.border_line.rounded_rectangle = (
                self.x, self.y, self.width, self.height,
                StosOSTheme.get_dimension('border_radius')
            )
    
    def _add_title(self):
        """Add title to panel"""
        title_label = StosOSLabel(
            text=self.title,
            label_type="title",
            size_hint_y=None,
            height=dp(40),
            halign="left"
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label, index=len(self.children))
    
    def animate_in(self, animation_type: str = "fade"):
        """Animate panel entrance"""
        if animation_type == "fade":
            StosOSAnimations.fade_in(self)
        elif animation_type == "slide":
            StosOSAnimations.slide_in_from_left(self)
        elif animation_type == "scale":
            StosOSAnimations.scale_in(self)


class StosOSCard(StosOSPanel):
    """
    Card component - elevated panel with shadow effect
    """
    
    def __init__(self, **kwargs):
        super().__init__(panel_type="elevated", **kwargs)
        
        # Add subtle shadow effect
        self._add_shadow()
    
    def _add_shadow(self):
        """Add shadow effect to card"""
        with self.canvas.before:
            # Shadow
            Color(*StosOSTheme.get_color('overlay_dark'))
            self.shadow_rect = RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[StosOSTheme.get_dimension('border_radius')]
            )
        
        self.bind(pos=self._update_shadow, size=self._update_shadow)
    
    def _update_shadow(self, *args):
        """Update shadow when widget changes"""
        if hasattr(self, 'shadow_rect'):
            self.shadow_rect.pos = (self.x + dp(2), self.y - dp(2))
            self.shadow_rect.size = self.size


class StosOSScrollView(ScrollView):
    """
    Styled scroll view with custom scrollbars
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Customize scrollbar appearance
        self.bar_color = StosOSTheme.get_color('accent_primary')
        self.bar_inactive_color = StosOSTheme.get_color('surface_variant')
        self.bar_width = dp(8)
        self.scroll_type = ['bars', 'content']


class StosOSPopup(Popup):
    """
    Styled popup with dark theme
    """
    
    def __init__(self, title: str = "", content_widget=None, **kwargs):
        # Apply theme styles
        kwargs.setdefault('background_color', StosOSTheme.get_color('surface'))
        kwargs.setdefault('title_color', StosOSTheme.get_color('text_primary'))
        kwargs.setdefault('title_font', StosOSTheme.get_font('mono_bold'))
        kwargs.setdefault('separator_color', StosOSTheme.get_color('border'))
        
        super().__init__(title=title, content=content_widget, **kwargs)
    
    def open_with_animation(self):
        """Open popup with animation"""
        self.open()
        StosOSAnimations.scale_in(self, duration=0.3)
    
    def dismiss_with_animation(self):
        """Dismiss popup with animation"""
        StosOSAnimations.scale_out(self, duration=0.2, callback=self.dismiss)


class StosOSLoadingOverlay(FloatLayout):
    """
    Loading overlay with spinner and message
    """
    
    def __init__(self, message: str = "Loading...", **kwargs):
        super().__init__(**kwargs)
        
        # Semi-transparent background
        with self.canvas.before:
            Color(*StosOSTheme.get_color('overlay_dark'))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Content container
        content = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(200), dp(100)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            spacing=StosOSTheme.get_spacing('md')
        )
        
        # Spinner
        from .animations import LoadingAnimations
        spinner = LoadingAnimations.create_spinner()
        spinner.pos_hint = {'center_x': 0.5}
        content.add_widget(spinner)
        
        # Message
        message_label = StosOSLabel(
            text=message,
            halign='center',
            size_hint_y=None,
            height=dp(30)
        )
        message_label.bind(size=message_label.setter('text_size'))
        content.add_widget(message_label)
        
        self.add_widget(content)
    
    def _update_bg(self, *args):
        """Update background rectangle"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
    
    def show(self, parent_widget):
        """Show loading overlay"""
        parent_widget.add_widget(self)
        StosOSAnimations.fade_in(self, duration=0.2)
    
    def hide(self):
        """Hide loading overlay"""
        def remove_widget():
            if self.parent:
                self.parent.remove_widget(self)
        
        StosOSAnimations.fade_out(self, duration=0.2, callback=remove_widget)


class StosOSIconButton(StosOSButton):
    """
    Icon-only button component
    """
    
    def __init__(self, icon: str, size: tuple = None, **kwargs):
        size = size or (dp(48), dp(48))
        
        super().__init__(
            text=icon,
            size_hint=(None, None),
            size=size,
            **kwargs
        )
        
        # Make it circular
        self.bind(pos=self._update_shape, size=self._update_shape)
    
    def _update_shape(self, *args):
        """Update to circular shape"""
        if hasattr(self, 'bg_rect'):
            # Make radius half of width for circular shape
            radius = min(self.width, self.height) / 2
            self.bg_rect.radius = [radius]


class StosOSToggleButton(StosOSButton):
    """
    Toggle button component with on/off states
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.is_toggled = False
        self.toggle_color = StosOSTheme.get_color('accent_primary')
        self.normal_color = self.background_color[:]
        
        # Override press behavior
        self.bind(on_press=self._on_toggle)
    
    def _on_toggle(self, *args):
        """Handle toggle state change"""
        self.is_toggled = not self.is_toggled
        
        if self.is_toggled:
            self.background_color = self.toggle_color
            StosOSAnimations.glow_effect(self, self.toggle_color)
        else:
            self.background_color = self.normal_color
    
    def set_state(self, toggled: bool):
        """Programmatically set toggle state"""
        if self.is_toggled != toggled:
            self._on_toggle()


# Export all components
__all__ = [
    'StosOSButton', 'StosOSLabel', 'StosOSTextInput', 'StosOSPanel', 
    'StosOSCard', 'StosOSScrollView', 'StosOSPopup', 'StosOSLoadingOverlay',
    'StosOSIconButton', 'StosOSToggleButton'
]