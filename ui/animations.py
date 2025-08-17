"""
StosOS Animation System
Smooth transitions and easing functions for UI components
"""

from typing import Callable, Optional, Dict, Any, Union
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.event import EventDispatcher

from .theme import StosOSTheme


class StosOSAnimations:
    """
    Animation utilities and presets for StosOS UI components
    """
    
    # Custom easing functions
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """Cubic ease-out function"""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_out_quart(t: float) -> float:
        """Quartic ease-out function"""
        return 1 - pow(1 - t, 4)
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        """Bounce ease-out function"""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375
    
    @classmethod
    def fade_in(cls, widget: Widget, duration: Optional[float] = None, 
                callback: Optional[Callable] = None) -> Animation:
        """
        Fade in animation
        
        Args:
            widget: Widget to animate
            duration: Animation duration (uses theme default if None)
            callback: Optional callback when animation completes
            
        Returns:
            Animation instance
        """
        duration = duration or StosOSTheme.get_animation_config('duration_normal')
        
        widget.opacity = 0
        anim = Animation(opacity=1, duration=duration, transition='out_cubic')
        
        if callback:
            anim.bind(on_complete=lambda *args: callback())
        
        anim.start(widget)
        return anim
    
    @classmethod
    def fade_out(cls, widget: Widget, duration: Optional[float] = None,
                 callback: Optional[Callable] = None) -> Animation:
        """
        Fade out animation
        
        Args:
            widget: Widget to animate
            duration: Animation duration (uses theme default if None)
            callback: Optional callback when animation completes
            
        Returns:
            Animation instance
        """
        duration = duration or StosOSTheme.get_animation_config('duration_normal')
        
        anim = Animation(opacity=0, duration=duration, transition='out_cubic')
        
        if callback:
            anim.bind(on_complete=lambda *args: callback())
        
        anim.start(widget)
        return anim
    
    @classmethod
    def slide_in_from_left(cls, widget: Widget, duration: Optional[float] = None,
                          callback: Optional[Callable] = None) -> Animation:
        """
        Slide in from left animation
        
        Args:
            widget: Widget to animate
            duration: Animation duration (uses theme default if None)
            callback: Optional callback when animation completes
            
        Returns:
            Animation instance
        """
        duration = duration or StosOSTheme.get_animation_config('duration_normal')
        
        original_x = widget.x
        widget.x = -widget.width
        widget.opacity = 0
        
        anim = Animation(x=original_x, opacity=1, duration=duration, transition='out_cubic')
        
        if callback:
            anim.bind(on_complete=lambda *args: callback())
        
        anim.start(widget)
        return anim
    
    @classmethod
    def slide_out_to_right(cls, widget: Widget, duration: Optional[float] = None,
                          callback: Optional[Callable] = None) -> Animation:
        """
        Slide out to right animation
        
        Args:
            widget: Widget to animate
            duration: Animation duration (uses theme default if None)
            callback: Optional callback when animation completes
            
        Returns:
            Animation instance
        """
        duration = duration or StosOSTheme.get_animation_config('duration_normal')
        
        target_x = widget.parent.width if widget.parent else widget.width
        
        anim = Animation(x=target_x, opacity=0, duration=duration, transition='out_cubic')
        
        if callback:
            anim.bind(on_complete=lambda *args: callback())
        
        anim.start(widget)
        return anim
    
    @classmethod
    def scale_in(cls, widget: Widget, duration: Optional[float] = None,
                 callback: Optional[Callable] = None) -> Animation:
        """
        Scale in animation (grow from center)
        
        Args:
            widget: Widget to animate
            duration: Animation duration (uses theme default if None)
            callback: Optional callback when animation completes
            
        Returns:
            Animation instance
        """
        duration = duration or StosOSTheme.get_animation_config('duration_normal')
        
        # Store original size
        original_size = widget.size[:]
        
        # Start small and transparent
        widget.size = (0, 0)
        widget.opacity = 0
        
        anim = Animation(
            size=original_size, 
            opacity=1, 
            duration=duration, 
            transition='out_bounce'
        )
        
        if callback:
            anim.bind(on_complete=lambda *args: callback())
        
        anim.start(widget)
        return anim
    
    @classmethod
    def scale_out(cls, widget: Widget, duration: Optional[float] = None,
                  callback: Optional[Callable] = None) -> Animation:
        """
        Scale out animation (shrink to center)
        
        Args:
            widget: Widget to animate
            duration: Animation duration (uses theme default if None)
            callback: Optional callback when animation completes
            
        Returns:
            Animation instance
        """
        duration = duration or StosOSTheme.get_animation_config('duration_fast')
        
        anim = Animation(
            size=(0, 0), 
            opacity=0, 
            duration=duration, 
            transition='out_cubic'
        )
        
        if callback:
            anim.bind(on_complete=lambda *args: callback())
        
        anim.start(widget)
        return anim
    
    @classmethod
    def pulse(cls, widget: Widget, scale: float = 1.1, duration: Optional[float] = None,
              repeat: bool = False) -> Animation:
        """
        Pulse animation (scale up and down)
        
        Args:
            widget: Widget to animate
            scale: Scale factor for pulse
            duration: Animation duration (uses theme default if None)
            repeat: Whether to repeat the animation
            
        Returns:
            Animation instance
        """
        duration = duration or StosOSTheme.get_animation_config('duration_fast')
        
        original_size = widget.size[:]
        pulse_size = (original_size[0] * scale, original_size[1] * scale)
        
        # Scale up then down
        anim_up = Animation(size=pulse_size, duration=duration/2, transition='out_cubic')
        anim_down = Animation(size=original_size, duration=duration/2, transition='out_cubic')
        
        # Chain animations
        anim = anim_up + anim_down
        
        if repeat:
            # Schedule repeat
            def repeat_pulse(*args):
                Clock.schedule_once(lambda dt: cls.pulse(widget, scale, duration, repeat), 0.1)
            anim.bind(on_complete=repeat_pulse)
        
        anim.start(widget)
        return anim
    
    @classmethod
    def glow_effect(cls, widget: Widget, glow_color: tuple = None, 
                   duration: Optional[float] = None) -> Animation:
        """
        Glow effect animation (color transition)
        
        Args:
            widget: Widget to animate
            glow_color: Color to glow (uses accent color if None)
            duration: Animation duration (uses theme default if None)
            
        Returns:
            Animation instance
        """
        duration = duration or StosOSTheme.get_animation_config('duration_slow')
        glow_color = glow_color or StosOSTheme.get_color('accent_primary')
        
        # Store original color
        original_color = getattr(widget, 'color', StosOSTheme.get_color('text_secondary'))
        
        # Animate to glow color and back
        anim_glow = Animation(color=glow_color, duration=duration/2, transition='out_cubic')
        anim_back = Animation(color=original_color, duration=duration/2, transition='out_cubic')
        
        anim = anim_glow + anim_back
        anim.start(widget)
        return anim
    
    @classmethod
    def typewriter_effect(cls, label_widget, text: str, duration: Optional[float] = None,
                         callback: Optional[Callable] = None) -> None:
        """
        Typewriter effect for text
        
        Args:
            label_widget: Label widget to animate
            text: Text to type out
            duration: Total duration for typing (uses theme default if None)
            callback: Optional callback when typing completes
        """
        duration = duration or StosOSTheme.get_animation_config('duration_slow')
        
        if not text:
            if callback:
                callback()
            return
        
        # Calculate delay between characters
        char_delay = duration / len(text)
        
        # Clear initial text
        label_widget.text = ""
        
        def add_character(char_index):
            if char_index < len(text):
                label_widget.text += text[char_index]
                Clock.schedule_once(lambda dt: add_character(char_index + 1), char_delay)
            elif callback:
                callback()
        
        # Start typing
        Clock.schedule_once(lambda dt: add_character(0), char_delay)


class LoadingAnimations:
    """
    Specialized loading animations for StosOS
    """
    
    @staticmethod
    def create_spinner(size: tuple = (32, 32)) -> Widget:
        """
        Create a spinning loading indicator
        
        Args:
            size: Size of the spinner
            
        Returns:
            Widget with spinning animation
        """
        from kivy.uix.label import Label
        
        spinner = Label(
            text="◐",
            font_size=size[0],
            color=StosOSTheme.get_color('accent_primary'),
            size_hint=(None, None),
            size=size
        )
        
        # Continuous rotation
        rotation_anim = Animation(
            angle=360, 
            duration=1.0, 
            transition='linear'
        )
        rotation_anim += Animation(angle=0, duration=0)  # Reset
        rotation_anim.repeat = True
        rotation_anim.start(spinner)
        
        return spinner
    
    @staticmethod
    def create_dots_loader(dot_count: int = 3) -> Widget:
        """
        Create animated dots loading indicator
        
        Args:
            dot_count: Number of dots
            
        Returns:
            Widget with dots animation
        """
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        
        container = BoxLayout(
            orientation='horizontal',
            size_hint=(None, None),
            spacing=StosOSTheme.get_spacing('sm')
        )
        
        dots = []
        for i in range(dot_count):
            dot = Label(
                text="●",
                font_size=StosOSTheme.get_font_size('body'),
                color=StosOSTheme.get_color('accent_primary'),
                size_hint=(None, None),
                size=(20, 20)
            )
            dots.append(dot)
            container.add_widget(dot)
        
        # Animate dots with staggered timing
        def animate_dot(dot_index):
            if dot_index < len(dots):
                dot = dots[dot_index]
                anim = Animation(opacity=0.3, duration=0.3) + Animation(opacity=1.0, duration=0.3)
                anim.bind(on_complete=lambda *args: Clock.schedule_once(
                    lambda dt: animate_dot((dot_index + 1) % len(dots)), 0.2))
                anim.start(dot)
        
        # Start animation
        Clock.schedule_once(lambda dt: animate_dot(0), 0)
        
        return container
    
    @staticmethod
    def create_progress_bar(width: float = 200) -> Widget:
        """
        Create animated progress bar
        
        Args:
            width: Width of the progress bar
            
        Returns:
            Widget with progress animation
        """
        from kivy.uix.progressbar import ProgressBar
        
        progress = ProgressBar(
            max=100,
            value=0,
            size_hint=(None, None),
            size=(width, 4)
        )
        
        # Animate progress
        anim = Animation(value=100, duration=2.0, transition='out_cubic')
        anim.repeat = True
        anim.start(progress)
        
        return progress