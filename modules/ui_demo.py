"""
UI Demo Module
Demonstrates the theme engine and UI components
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock

from core.base_module import BaseModule
from ui.theme import StosOSTheme
from ui.components import (
    StosOSButton, StosOSLabel, StosOSTextInput, StosOSPanel, 
    StosOSCard, StosOSScrollView, StosOSLoadingOverlay,
    StosOSIconButton, StosOSToggleButton
)
from ui.animations import StosOSAnimations, LoadingAnimations


class UIDemoModule(BaseModule):
    """
    Demo module showcasing UI components and animations
    """
    
    def __init__(self):
        super().__init__(
            module_id="ui_demo",
            display_name="UI Demo",
            icon="🎨"
        )
        self.loading_overlay = None
    
    def initialize(self) -> bool:
        """Initialize the UI demo module"""
        try:
            self.logger.info("Initializing UI Demo module")
            self._initialized = True
            return True
        except Exception as e:
            self.handle_error(e, "UI Demo initialization")
            return False
    
    def get_screen(self) -> Screen:
        """Create and return the demo screen"""
        screen = Screen()
        
        # Main container with theme background
        main_container = BoxLayout(
            orientation='vertical',
            padding=StosOSTheme.get_spacing('md'),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        # Set background color
        with main_container.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*StosOSTheme.get_color('background'))
            self.bg_rect = Rectangle(pos=main_container.pos, size=main_container.size)
        
        main_container.bind(
            pos=lambda instance, value: setattr(self.bg_rect, 'pos', value),
            size=lambda instance, value: setattr(self.bg_rect, 'size', value)
        )
        
        # Title
        title = StosOSLabel(
            text="StosOS UI Components Demo",
            label_type="title",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('button_height'),
            halign='center'
        )
        title.bind(size=title.setter('text_size'))
        main_container.add_widget(title)
        
        # Scrollable content
        scroll = StosOSScrollView()
        content = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('md'),
            size_hint_y=None,
            padding=[0, 0, 0, StosOSTheme.get_spacing('xl')]
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Buttons section
        self._add_buttons_section(content)
        
        # Input section
        self._add_input_section(content)
        
        # Panels section
        self._add_panels_section(content)
        
        # Animation section
        self._add_animation_section(content)
        
        scroll.add_widget(content)
        main_container.add_widget(scroll)
        
        screen.add_widget(main_container)
        self.screen_widget = screen
        
        return screen
    
    def _add_buttons_section(self, parent):
        """Add buttons demonstration section"""
        section = StosOSCard(title="Buttons")
        section.size_hint_y = None
        section.height = StosOSTheme.get_spacing('xxl') * 4
        
        button_grid = GridLayout(
            cols=2,
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None,
            height=StosOSTheme.get_dimension('button_height') * 3 + StosOSTheme.get_spacing('sm') * 2
        )
        
        # Primary button
        primary_btn = StosOSButton(
            text="Primary Button",
            button_type="primary",
            on_press_callback=lambda: self._show_message("Primary button pressed!")
        )
        button_grid.add_widget(primary_btn)
        
        # Secondary button
        secondary_btn = StosOSButton(
            text="Secondary Button",
            button_type="secondary",
            on_press_callback=lambda: self._show_message("Secondary button pressed!")
        )
        button_grid.add_widget(secondary_btn)
        
        # Accent button
        accent_btn = StosOSButton(
            text="Accent Button",
            button_type="accent",
            on_press_callback=lambda: self._show_message("Accent button pressed!")
        )
        button_grid.add_widget(accent_btn)
        
        # Danger button
        danger_btn = StosOSButton(
            text="Danger Button",
            button_type="danger",
            on_press_callback=lambda: self._show_message("Danger button pressed!")
        )
        button_grid.add_widget(danger_btn)
        
        # Icon button
        icon_btn = StosOSIconButton(
            icon="⚙",
            on_press_callback=lambda: self._show_message("Settings clicked!")
        )
        button_grid.add_widget(icon_btn)
        
        # Toggle button
        toggle_btn = StosOSToggleButton(
            text="Toggle Me",
            on_press_callback=lambda: self._show_message(f"Toggle: {'ON' if toggle_btn.is_toggled else 'OFF'}")
        )
        button_grid.add_widget(toggle_btn)
        
        section.add_widget(button_grid)
        parent.add_widget(section)
    
    def _add_input_section(self, parent):
        """Add input components section"""
        section = StosOSCard(title="Input Components")
        section.size_hint_y = None
        section.height = StosOSTheme.get_spacing('xxl') * 3
        
        input_container = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height') * 2 + StosOSTheme.get_spacing('sm')
        )
        
        # Text input
        text_input = StosOSTextInput(
            placeholder="Enter some text...",
            multiline=False
        )
        input_container.add_widget(text_input)
        
        # Multiline input
        multiline_input = StosOSTextInput(
            placeholder="Enter multiple lines...",
            multiline=True
        )
        input_container.add_widget(multiline_input)
        
        section.add_widget(input_container)
        parent.add_widget(section)
    
    def _add_panels_section(self, parent):
        """Add panels demonstration section"""
        panels_container = BoxLayout(
            orientation='horizontal',
            spacing=StosOSTheme.get_spacing('md'),
            size_hint_y=None,
            height=StosOSTheme.get_spacing('xxl') * 3
        )
        
        # Default panel
        default_panel = StosOSPanel(
            title="Default Panel",
            size_hint_x=0.5
        )
        default_panel.add_widget(StosOSLabel(
            text="This is a default panel with standard styling.",
            halign='center'
        ))
        panels_container.add_widget(default_panel)
        
        # Outlined panel
        outlined_panel = StosOSPanel(
            title="Outlined Panel",
            panel_type="outlined",
            size_hint_x=0.5
        )
        outlined_panel.add_widget(StosOSLabel(
            text="This is an outlined panel with border styling.",
            halign='center'
        ))
        panels_container.add_widget(outlined_panel)
        
        parent.add_widget(panels_container)
    
    def _add_animation_section(self, parent):
        """Add animations demonstration section"""
        section = StosOSCard(title="Animations & Effects")
        section.size_hint_y = None
        section.height = StosOSTheme.get_spacing('xxl') * 4
        
        animation_grid = GridLayout(
            cols=2,
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None,
            height=StosOSTheme.get_dimension('button_height') * 3 + StosOSTheme.get_spacing('sm') * 2
        )
        
        # Fade animation
        fade_btn = StosOSButton(
            text="Fade Animation",
            on_press_callback=self._demo_fade_animation
        )
        animation_grid.add_widget(fade_btn)
        
        # Slide animation
        slide_btn = StosOSButton(
            text="Slide Animation",
            on_press_callback=self._demo_slide_animation
        )
        animation_grid.add_widget(slide_btn)
        
        # Scale animation
        scale_btn = StosOSButton(
            text="Scale Animation",
            on_press_callback=self._demo_scale_animation
        )
        animation_grid.add_widget(scale_btn)
        
        # Pulse animation
        pulse_btn = StosOSButton(
            text="Pulse Animation",
            on_press_callback=self._demo_pulse_animation
        )
        animation_grid.add_widget(pulse_btn)
        
        # Typewriter effect
        typewriter_btn = StosOSButton(
            text="Typewriter Effect",
            on_press_callback=self._demo_typewriter_effect
        )
        animation_grid.add_widget(typewriter_btn)
        
        # Loading overlay
        loading_btn = StosOSButton(
            text="Loading Overlay",
            on_press_callback=self._demo_loading_overlay
        )
        animation_grid.add_widget(loading_btn)
        
        section.add_widget(animation_grid)
        parent.add_widget(section)
        
        # Demo label for animations
        self.demo_label = StosOSLabel(
            text="Animation demo area",
            halign='center',
            size_hint_y=None,
            height=StosOSTheme.get_dimension('button_height')
        )
        self.demo_label.bind(size=self.demo_label.setter('text_size'))
        section.add_widget(self.demo_label)
    
    def _show_message(self, message: str):
        """Show a message using label animation"""
        if hasattr(self, 'demo_label'):
            self.demo_label.animate_text_change(message)
            # Reset after 2 seconds
            Clock.schedule_once(
                lambda dt: self.demo_label.animate_text_change("Animation demo area"), 
                2.0
            )
    
    def _demo_fade_animation(self):
        """Demonstrate fade animation"""
        if hasattr(self, 'demo_label'):
            StosOSAnimations.fade_out(
                self.demo_label, 
                callback=lambda: StosOSAnimations.fade_in(self.demo_label)
            )
    
    def _demo_slide_animation(self):
        """Demonstrate slide animation"""
        if hasattr(self, 'demo_label'):
            StosOSAnimations.slide_out_to_right(
                self.demo_label,
                callback=lambda: StosOSAnimations.slide_in_from_left(self.demo_label)
            )
    
    def _demo_scale_animation(self):
        """Demonstrate scale animation"""
        if hasattr(self, 'demo_label'):
            StosOSAnimations.scale_out(
                self.demo_label,
                callback=lambda: StosOSAnimations.scale_in(self.demo_label)
            )
    
    def _demo_pulse_animation(self):
        """Demonstrate pulse animation"""
        if hasattr(self, 'demo_label'):
            StosOSAnimations.pulse(self.demo_label, scale=1.2, duration=0.6)
    
    def _demo_typewriter_effect(self):
        """Demonstrate typewriter effect"""
        if hasattr(self, 'demo_label'):
            StosOSAnimations.typewriter_effect(
                self.demo_label,
                "This text appears with typewriter effect!",
                duration=2.0
            )
    
    def _demo_loading_overlay(self):
        """Demonstrate loading overlay"""
        if self.screen_widget and not self.loading_overlay:
            self.loading_overlay = StosOSLoadingOverlay(
                message="Loading demo content..."
            )
            self.loading_overlay.show(self.screen_widget)
            
            # Hide after 3 seconds
            Clock.schedule_once(self._hide_loading_overlay, 3.0)
    
    def _hide_loading_overlay(self, dt):
        """Hide the loading overlay"""
        if self.loading_overlay:
            self.loading_overlay.hide()
            self.loading_overlay = None
    
    def on_activate(self):
        """Called when module becomes active"""
        super().on_activate()
        self.logger.info("UI Demo module activated")
        
        # Animate in the screen content
        if self.screen_widget:
            for child in self.screen_widget.children:
                StosOSAnimations.fade_in(child, duration=0.5)
    
    def on_deactivate(self):
        """Called when module becomes inactive"""
        super().on_deactivate()
        self.logger.info("UI Demo module deactivated")
        
        # Hide loading overlay if active
        if self.loading_overlay:
            self._hide_loading_overlay(None)
    
    def cleanup(self):
        """Cleanup module resources"""
        super().cleanup()
        if self.loading_overlay:
            self._hide_loading_overlay(None)