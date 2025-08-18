"""
StosOS Branding Screen
Animated startup sequence with "StosOS X" branding and system initialization
"""

import logging
from typing import Callable, Optional
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

from .theme import StosOSTheme
from .animations import StosOSAnimations


class BrandingScreen(FloatLayout):
    """
    Animated branding screen for StosOS startup sequence
    """
    
    def __init__(self, on_complete: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        
        self.logger = logging.getLogger(__name__)
        self.on_complete_callback = on_complete
        self.animation_failed = False
        self.initialization_steps = [
            "Initializing core systems...",
            "Loading configuration...",
            "Starting modules...",
            "Preparing interface...",
            "Ready!"
        ]
        self.current_step = 0
        
        # Setup background
        self._setup_background()
        
        # Create UI elements
        self._create_branding_elements()
        self._create_progress_elements()
        
        # Start animation sequence
        Clock.schedule_once(self._start_animation_sequence, 0.5)
    
    def _setup_background(self):
        """Setup the dark background"""
        with self.canvas.before:
            Color(*StosOSTheme.get_color('background'))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_background, size=self._update_background)
    
    def _update_background(self, *args):
        """Update background when screen size changes"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
    
    def _create_branding_elements(self):
        """Create the main branding elements"""
        # Main container for branding
        self.branding_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(400), dp(200)),
            pos_hint={'center_x': 0.5, 'center_y': 0.6},
            spacing=StosOSTheme.get_spacing('lg')
        )
        
        # Main title - "StosOS X"
        self.main_title = Label(
            text="",  # Start empty for typewriter effect
            font_size=StosOSTheme.get_font_size('display'),
            color=StosOSTheme.get_color('text_primary'),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(80)
        )
        self.main_title.bind(size=self.main_title.setter('text_size'))
        
        # Subtitle
        self.subtitle = Label(
            text="",  # Start empty
            font_size=StosOSTheme.get_font_size('body_large'),
            color=StosOSTheme.get_color('text_secondary'),
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(40),
            opacity=0  # Start invisible
        )
        self.subtitle.bind(size=self.subtitle.setter('text_size'))
        
        # Add to container
        self.branding_container.add_widget(self.main_title)
        self.branding_container.add_widget(self.subtitle)
        
        # Add container to screen
        self.add_widget(self.branding_container)
        
        # Initially hide the container for fade-in effect
        self.branding_container.opacity = 0
    
    def _create_progress_elements(self):
        """Create progress indicators"""
        # Progress container
        self.progress_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, None),
            size=(dp(300), dp(80)),
            pos_hint={'center_x': 0.5, 'center_y': 0.3},
            spacing=StosOSTheme.get_spacing('md'),
            opacity=0  # Start invisible
        )
        
        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(4)
        )
        
        # Status text
        self.status_label = Label(
            text="",
            font_size=StosOSTheme.get_font_size('body'),
            color=StosOSTheme.get_color('text_hint'),
            halign='center',
            size_hint_y=None,
            height=dp(30)
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        
        # Add to container
        self.progress_container.add_widget(self.progress_bar)
        self.progress_container.add_widget(self.status_label)
        
        # Add to screen
        self.add_widget(self.progress_container)
    
    def _start_animation_sequence(self, dt):
        """Start the complete animation sequence"""
        try:
            self.logger.info("Starting branding animation sequence")
            
            # Phase 1: Fade in branding container
            StosOSAnimations.fade_in(
                self.branding_container, 
                duration=0.8, 
                callback=self._start_title_animation
            )
            
        except Exception as e:
            self.logger.error(f"Failed to start animation sequence: {e}")
            self._handle_animation_failure()
    
    def _start_title_animation(self):
        """Start the title typewriter animation"""
        try:
            # Typewriter effect for main title
            StosOSAnimations.typewriter_effect(
                self.main_title,
                "StosOS X",
                duration=1.5,
                callback=self._start_subtitle_animation
            )
            
        except Exception as e:
            self.logger.error(f"Failed to animate title: {e}")
            self.main_title.text = "StosOS X"  # Fallback
            self._start_subtitle_animation()
    
    def _start_subtitle_animation(self):
        """Start the subtitle animation"""
        try:
            # Set subtitle text and fade in
            self.subtitle.text = "Desktop Environment"
            StosOSAnimations.fade_in(
                self.subtitle,
                duration=0.6,
                callback=self._start_progress_animation
            )
            
        except Exception as e:
            self.logger.error(f"Failed to animate subtitle: {e}")
            self.subtitle.opacity = 1  # Fallback
            self._start_progress_animation()
    
    def _start_progress_animation(self):
        """Start the progress indicators"""
        try:
            # Fade in progress container
            StosOSAnimations.fade_in(
                self.progress_container,
                duration=0.4,
                callback=self._start_initialization_sequence
            )
            
        except Exception as e:
            self.logger.error(f"Failed to show progress: {e}")
            self.progress_container.opacity = 1  # Fallback
            self._start_initialization_sequence()
    
    def _start_initialization_sequence(self):
        """Start the system initialization simulation"""
        try:
            self.logger.info("Starting initialization sequence")
            self._update_initialization_step()
            
        except Exception as e:
            self.logger.error(f"Failed to start initialization: {e}")
            self._complete_sequence()
    
    def _update_initialization_step(self):
        """Update the current initialization step"""
        try:
            if self.current_step < len(self.initialization_steps):
                # Update status text
                step_text = self.initialization_steps[self.current_step]
                self.status_label.text = step_text
                
                # Calculate progress
                progress = ((self.current_step + 1) / len(self.initialization_steps)) * 100
                
                # Animate progress bar
                progress_anim = Animation(
                    value=progress,
                    duration=0.8,
                    transition='out_cubic'
                )
                progress_anim.start(self.progress_bar)
                
                # Schedule next step
                self.current_step += 1
                Clock.schedule_once(
                    lambda dt: self._update_initialization_step(),
                    1.0  # 1 second between steps
                )
            else:
                # All steps complete
                Clock.schedule_once(lambda dt: self._complete_sequence(), 0.5)
                
        except Exception as e:
            self.logger.error(f"Failed to update initialization step: {e}")
            self._complete_sequence()
    
    def _complete_sequence(self):
        """Complete the branding sequence and transition"""
        try:
            self.logger.info("Branding sequence complete, transitioning to main interface")
            
            # Fade out all elements
            fade_duration = 0.6
            
            StosOSAnimations.fade_out(self.branding_container, duration=fade_duration)
            StosOSAnimations.fade_out(
                self.progress_container, 
                duration=fade_duration,
                callback=self._finish_branding
            )
            
        except Exception as e:
            self.logger.error(f"Failed to complete sequence: {e}")
            self._finish_branding()
    
    def _finish_branding(self):
        """Finish branding and call completion callback"""
        try:
            if self.on_complete_callback:
                self.on_complete_callback()
            else:
                self.logger.warning("No completion callback provided")
                
        except Exception as e:
            self.logger.error(f"Error in completion callback: {e}")
    
    def _handle_animation_failure(self):
        """Handle animation failure with fallback"""
        self.logger.warning("Animation failed, using fallback display")
        self.animation_failed = True
        
        try:
            # Show static branding immediately
            self.branding_container.opacity = 1
            self.main_title.text = "StosOS X"
            self.subtitle.text = "Desktop Environment"
            self.subtitle.opacity = 1
            
            # Show progress at 100%
            self.progress_container.opacity = 1
            self.progress_bar.value = 100
            self.status_label.text = "Ready!"
            
            # Complete after short delay
            Clock.schedule_once(lambda dt: self._finish_branding(), 2.0)
            
        except Exception as e:
            self.logger.error(f"Fallback also failed: {e}")
            # Last resort - just call completion
            Clock.schedule_once(lambda dt: self._finish_branding(), 0.1)
    
    def skip_animation(self):
        """Skip animation and go directly to completion"""
        self.logger.info("Skipping branding animation")
        
        # Cancel any scheduled events
        Clock.unschedule(self._update_initialization_step)
        
        # Show final state immediately
        self._handle_animation_failure()


class BrandingScreenManager:
    """
    Manager for the branding screen lifecycle
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.branding_screen = None
        self.is_showing = False
    
    def show_branding(self, parent_widget, on_complete: Optional[Callable] = None) -> bool:
        """
        Show the branding screen
        
        Args:
            parent_widget: Parent widget to add branding screen to
            on_complete: Callback when branding is complete
            
        Returns:
            bool: True if branding started successfully
        """
        try:
            if self.is_showing:
                self.logger.warning("Branding screen already showing")
                return False
            
            self.logger.info("Showing branding screen")
            
            # Create branding screen
            self.branding_screen = BrandingScreen(on_complete=self._on_branding_complete)
            self._completion_callback = on_complete
            
            # Add to parent
            parent_widget.add_widget(self.branding_screen)
            self.is_showing = True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to show branding screen: {e}")
            return False
    
    def _on_branding_complete(self):
        """Handle branding completion"""
        try:
            self.logger.info("Branding screen completed")
            
            # Remove branding screen
            if self.branding_screen and self.branding_screen.parent:
                self.branding_screen.parent.remove_widget(self.branding_screen)
            
            self.is_showing = False
            
            # Call external completion callback
            if self._completion_callback:
                self._completion_callback()
                
        except Exception as e:
            self.logger.error(f"Error completing branding: {e}")
    
    def skip_branding(self):
        """Skip the branding animation"""
        if self.branding_screen and self.is_showing:
            self.branding_screen.skip_animation()
    
    def is_branding_active(self) -> bool:
        """Check if branding is currently active"""
        return self.is_showing