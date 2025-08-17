"""
Main Dashboard Module for StosOS

Provides the main dashboard interface with:
- Module tiles and quick access buttons
- Smooth navigation system between all modules with animated transitions
- Status indicators for each module (connectivity, notifications, etc.)
- Global search functionality across all modules
- Settings panel for system configuration and preferences

Requirements: 9.1, 9.2, 9.3
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.animation import Animation

from core.base_module import BaseModule
from core.database_manager import DatabaseManager
from ui.components import (
    StosOSButton, StosOSLabel, StosOSTextInput, StosOSPanel, 
    StosOSCard, StosOSScrollView, StosOSPopup, StosOSLoadingOverlay,
    StosOSIconButton, StosOSToggleButton
)
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations


class ModuleTile(StosOSCard):
    """Individual module tile component"""
    
    def __init__(self, module_info: Dict[str, Any], on_click: Callable = None, **kwargs):
        super().__init__(**kwargs)
        
        self.module_info = module_info
        self.on_click = on_click
        
        self.size_hint = (None, None)
        self.size = (dp(180), dp(140))
        
        self._setup_tile_content()
        
        # Bind click event
        self.bind(on_touch_down=self._on_tile_click)
    
    def _setup_tile_content(self):
        """Setup the content of the module tile"""
        # Main container
        container = BoxLayout(
            orientation='vertical',
            padding=StosOSTheme.get_spacing('md'),
            spacing=StosOSTheme.get_spacing('sm')
        )
        
        # Header with icon and status
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=StosOSTheme.get_spacing('sm')
        )
        
        # Module icon
        icon_label = StosOSLabel(
            text=self.module_info.get('icon', '●'),
            font_size=str(StosOSTheme.get_font_size('display')) + 'sp',
            color=StosOSTheme.get_color('accent_primary'),
            size_hint_x=None,
            width=dp(40),
            halign='center'
        )
        header.add_widget(icon_label)
        
        # Status indicator
        status = self.module_info.get('status', {})
        status_color = StosOSTheme.get_color('success') if status.get('connected', True) else StosOSTheme.get_color('error')
        
        status_indicator = StosOSLabel(
            text='●',
            font_size='12sp',
            color=status_color,
            size_hint_x=None,
            width=dp(20),
            halign='center'
        )
        header.add_widget(status_indicator)
        
        container.add_widget(header)
        
        # Module name
        name_label = StosOSLabel(
            text=self.module_info.get('display_name', 'Unknown'),
            font_size=str(StosOSTheme.get_font_size('title')) + 'sp',
            color=StosOSTheme.get_color('text_primary'),
            halign='center',
            size_hint_y=None,
            height=dp(30)
        )
        name_label.bind(size=name_label.setter('text_size'))
        container.add_widget(name_label)
        
        # Module description
        description = self.module_info.get('description', '')
        if description:
            desc_label = StosOSLabel(
                text=description,
                font_size=str(StosOSTheme.get_font_size('caption')) + 'sp',
                color=StosOSTheme.get_color('text_secondary'),
                halign='center',
                text_size=(dp(160), None),
                size_hint_y=None,
                height=dp(40)
            )
            container.add_widget(desc_label)
        
        # Notification badge (if any)
        notifications = status.get('notifications', 0)
        if notifications > 0:
            badge = StosOSLabel(
                text=str(notifications),
                font_size='10sp',
                color=StosOSTheme.get_color('text_secondary'),
                size_hint=(None, None),
                size=(dp(20), dp(20)),
                pos_hint={'right': 0.95, 'top': 0.95}
            )
            # Add badge as overlay
            overlay = FloatLayout()
            overlay.add_widget(badge)
            container.add_widget(overlay)
        
        self.add_widget(container)
    
    def _on_tile_click(self, touch):
        """Handle tile click"""
        if self.collide_point(*touch.pos):
            # Animate click
            StosOSAnimations.pulse(self, scale=0.95, duration=0.1)
            
            # Execute callback
            if self.on_click:
                Clock.schedule_once(lambda dt: self.on_click(self.module_info), 0.1)
            
            return True
        return False
    
    def update_status(self, status: Dict[str, Any]):
        """Update the status of the module tile"""
        self.module_info['status'] = status
        # Refresh tile content
        self.clear_widgets()
        self._setup_tile_content()


class QuickActionBar(BoxLayout):
    """Quick action bar with frequently used functions"""
    
    def __init__(self, on_search: Callable = None, on_settings: Callable = None, 
                 on_power: Callable = None, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = StosOSTheme.get_spacing('md')
        self.spacing = StosOSTheme.get_spacing('md')
        
        # Search button
        search_btn = StosOSIconButton(
            icon='🔍',
            size=(dp(50), dp(50)),
            button_type='secondary'
        )
        if on_search:
            search_btn.bind(on_press=lambda x: on_search())
        self.add_widget(search_btn)
        
        # Spacer
        self.add_widget(BoxLayout())
        
        # Current time display
        self.time_label = StosOSLabel(
            text=datetime.now().strftime('%H:%M'),
            font_size=str(StosOSTheme.get_font_size('title')) + 'sp',
            color=StosOSTheme.get_color('text_primary'),
            size_hint_x=None,
            width=dp(80),
            halign='center'
        )
        self.add_widget(self.time_label)
        
        # Update time every minute
        Clock.schedule_interval(self._update_time, 60)
        
        # Spacer
        self.add_widget(BoxLayout())
        
        # Settings button
        settings_btn = StosOSIconButton(
            icon='⚙️',
            size=(dp(50), dp(50)),
            button_type='secondary'
        )
        if on_settings:
            settings_btn.bind(on_press=lambda x: on_settings())
        self.add_widget(settings_btn)
        
        # Power button
        power_btn = StosOSIconButton(
            icon='⏻',
            size=(dp(50), dp(50)),
            button_type='danger'
        )
        if on_power:
            power_btn.bind(on_press=lambda x: on_power())
        self.add_widget(power_btn)
    
    def _update_time(self, dt):
        """Update the time display"""
        self.time_label.text = datetime.now().strftime('%H:%M')


class GlobalSearchOverlay(FloatLayout):
    """Global search overlay with results from all modules"""
    
    def __init__(self, on_close: Callable = None, on_result_select: Callable = None, **kwargs):
        super().__init__(**kwargs)
        
        self.on_close = on_close
        self.on_result_select = on_result_select
        
        # Semi-transparent background
        from kivy.graphics import Color, Rectangle
        with self.canvas.before:
            Color(*StosOSTheme.get_color('overlay_dark'))
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Search container
        search_container = StosOSPanel(
            title="Global Search",
            size_hint=(0.8, 0.8),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Search input
        self.search_input = StosOSTextInput(
            placeholder="Search across all modules...",
            size_hint_y=None,
            height=dp(50),
            multiline=False
        )
        self.search_input.bind(text=self._on_search_text_change)
        search_container.add_widget(self.search_input)
        
        # Results scroll view
        self.results_scroll = StosOSScrollView()
        self.results_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=StosOSTheme.get_spacing('sm')
        )
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        self.results_scroll.add_widget(self.results_container)
        search_container.add_widget(self.results_scroll)
        
        # Close button
        close_btn = StosOSButton(
            text="Close",
            size_hint_y=None,
            height=dp(40),
            button_type='secondary'
        )
        close_btn.bind(on_press=self._close_search)
        search_container.add_widget(close_btn)
        
        self.add_widget(search_container)
        
        # Focus search input
        Clock.schedule_once(lambda dt: setattr(self.search_input, 'focus', True), 0.1)
    
    def _update_bg(self, *args):
        """Update background rectangle"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
    
    def _on_search_text_change(self, instance, text):
        """Handle search text changes"""
        if len(text) >= 2:  # Start searching after 2 characters
            Clock.unschedule(self._perform_search)
            Clock.schedule_once(lambda dt: self._perform_search(text), 0.5)
        else:
            self._clear_results()
    
    def _perform_search(self, query: str):
        """Perform search across all modules"""
        # Clear previous results
        self._clear_results()
        
        # Mock search results for demonstration
        # In a real implementation, this would query all registered modules
        mock_results = [
            {
                'module': 'Tasks',
                'type': 'Task',
                'title': f'Task containing "{query}"',
                'description': 'Complete physics homework',
                'module_id': 'task_manager'
            },
            {
                'module': 'Ideas',
                'type': 'Idea',
                'title': f'Idea about "{query}"',
                'description': 'Revolutionary app concept',
                'module_id': 'idea_board'
            },
            {
                'module': 'Calendar',
                'type': 'Event',
                'title': f'Event: "{query}" meeting',
                'description': 'Tomorrow at 3 PM',
                'module_id': 'calendar_module'
            }
        ]
        
        # Add results to container
        for result in mock_results:
            result_card = self._create_result_card(result)
            self.results_container.add_widget(result_card)
    
    def _create_result_card(self, result: Dict[str, Any]) -> StosOSCard:
        """Create a search result card"""
        card = StosOSCard(
            size_hint_y=None,
            height=dp(80)
        )
        
        container = BoxLayout(
            orientation='horizontal',
            padding=StosOSTheme.get_spacing('sm'),
            spacing=StosOSTheme.get_spacing('sm')
        )
        
        # Result info
        info_container = BoxLayout(orientation='vertical')
        
        title_label = StosOSLabel(
            text=result['title'],
            font_size=str(StosOSTheme.get_font_size('body')) + 'sp',
            color=StosOSTheme.get_color('text_primary'),
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        info_container.add_widget(title_label)
        
        desc_label = StosOSLabel(
            text=f"{result['module']} • {result['description']}",
            font_size=str(StosOSTheme.get_font_size('caption')) + 'sp',
            color=StosOSTheme.get_color('text_secondary'),
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        info_container.add_widget(desc_label)
        
        container.add_widget(info_container)
        
        # Open button
        open_btn = StosOSButton(
            text="Open",
            size_hint_x=None,
            width=dp(80),
            button_type='accent'
        )
        open_btn.bind(on_press=lambda x: self._select_result(result))
        container.add_widget(open_btn)
        
        card.add_widget(container)
        return card
    
    def _select_result(self, result: Dict[str, Any]):
        """Handle result selection"""
        if self.on_result_select:
            self.on_result_select(result)
        self._close_search()
    
    def _clear_results(self):
        """Clear search results"""
        self.results_container.clear_widgets()
    
    def _close_search(self, *args):
        """Close search overlay"""
        if self.on_close:
            self.on_close()


class SettingsPanel(StosOSPanel):
    """Settings panel for system configuration"""
    
    def __init__(self, config_manager, on_close: Callable = None, **kwargs):
        super().__init__(title="System Settings", **kwargs)
        
        self.config_manager = config_manager
        self.on_close = on_close
        
        self._setup_settings_content()
    
    def _setup_settings_content(self):
        """Setup settings panel content"""
        # Settings scroll view
        scroll = StosOSScrollView()
        settings_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=StosOSTheme.get_spacing('md'),
            padding=StosOSTheme.get_spacing('md')
        )
        settings_container.bind(minimum_height=settings_container.setter('height'))
        
        # Theme settings
        theme_section = self._create_settings_section("Theme", [
            ("Dark Mode", "theme.dark_mode", True, "toggle"),
            ("Accent Color", "theme.accent_color", "#00ff41", "color"),
            ("Animation Speed", "theme.animation_speed", 1.0, "slider")
        ])
        settings_container.add_widget(theme_section)
        
        # Power settings
        power_section = self._create_settings_section("Power Management", [
            ("Dim Timeout (seconds)", "power.dim_timeout", 30, "number"),
            ("Sleep Timeout (seconds)", "power.sleep_timeout", 60, "number"),
            ("Voice Wake", "power.enable_voice_wake", True, "toggle")
        ])
        settings_container.add_widget(power_section)
        
        # Module settings
        module_section = self._create_settings_section("Modules", [
            ("Auto-refresh Calendar", "modules.calendar.auto_refresh", True, "toggle"),
            ("Task Notifications", "modules.tasks.notifications", True, "toggle"),
            ("Voice Assistant", "modules.voice.enabled", False, "toggle")
        ])
        settings_container.add_widget(module_section)
        
        # Action buttons
        actions = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        save_btn = StosOSButton(
            text="Save Settings",
            button_type='accent'
        )
        save_btn.bind(on_press=self._save_settings)
        actions.add_widget(save_btn)
        
        reset_btn = StosOSButton(
            text="Reset to Defaults",
            button_type='secondary'
        )
        reset_btn.bind(on_press=self._reset_settings)
        actions.add_widget(reset_btn)
        
        close_btn = StosOSButton(
            text="Close",
            button_type='secondary'
        )
        close_btn.bind(on_press=lambda x: self.on_close() if self.on_close else None)
        actions.add_widget(close_btn)
        
        settings_container.add_widget(actions)
        
        scroll.add_widget(settings_container)
        self.add_widget(scroll)
    
    def _create_settings_section(self, title: str, settings: List[tuple]) -> StosOSCard:
        """Create a settings section card"""
        section = StosOSCard(
            size_hint_y=None,
            height=dp(60 + len(settings) * 50)
        )
        
        container = BoxLayout(
            orientation='vertical',
            padding=StosOSTheme.get_spacing('md'),
            spacing=StosOSTheme.get_spacing('sm')
        )
        
        # Section title
        title_label = StosOSLabel(
            text=title,
            font_size=str(StosOSTheme.get_font_size('title')) + 'sp',
            color=StosOSTheme.get_color('accent_primary'),
            size_hint_y=None,
            height=dp(30),
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        container.add_widget(title_label)
        
        # Settings items
        for setting_name, setting_key, default_value, setting_type in settings:
            item = self._create_setting_item(setting_name, setting_key, default_value, setting_type)
            container.add_widget(item)
        
        section.add_widget(container)
        return section
    
    def _create_setting_item(self, name: str, key: str, default_value: Any, setting_type: str) -> BoxLayout:
        """Create an individual setting item"""
        item = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        # Setting name
        name_label = StosOSLabel(
            text=name,
            color=StosOSTheme.get_color('text_primary'),
            halign='left'
        )
        name_label.bind(size=name_label.setter('text_size'))
        item.add_widget(name_label)
        
        # Setting control based on type
        current_value = self.config_manager.get(key, default_value)
        
        if setting_type == "toggle":
            control = StosOSToggleButton(
                text="ON" if current_value else "OFF",
                size_hint_x=None,
                width=dp(80)
            )
            control.set_state(current_value)
            control.bind(on_press=lambda x, k=key: self._update_setting(k, control.is_toggled))
        
        elif setting_type == "number":
            control = StosOSTextInput(
                text=str(current_value),
                size_hint_x=None,
                width=dp(100),
                input_filter='float'
            )
            control.bind(text=lambda x, text, k=key: self._update_setting(k, float(text) if text else 0))
        
        elif setting_type == "color":
            control = StosOSButton(
                text=str(current_value),
                size_hint_x=None,
                width=dp(120),
                button_type='secondary'
            )
            # Color picker would be implemented here
        
        else:  # Default to text input
            control = StosOSTextInput(
                text=str(current_value),
                size_hint_x=None,
                width=dp(150)
            )
            control.bind(text=lambda x, text, k=key: self._update_setting(k, text))
        
        item.add_widget(control)
        return item
    
    def _update_setting(self, key: str, value: Any):
        """Update a setting value"""
        self.config_manager.set(key, value)
    
    def _save_settings(self, *args):
        """Save all settings"""
        self.config_manager.save()
        # Show confirmation
        # In a real implementation, this would show a toast or notification
    
    def _reset_settings(self, *args):
        """Reset settings to defaults"""
        # Show confirmation dialog
        # In a real implementation, this would show a confirmation popup
        pass


class DashboardModule(BaseModule):
    """Main Dashboard Module"""
    
    def __init__(self):
        super().__init__(
            module_id="dashboard",
            display_name="Dashboard",
            icon="🏠"
        )
        
        self.description = "Main system dashboard"
        
        self.logger = logging.getLogger(__name__)
        self.db_manager = None
        self.screen = None
        self.search_overlay = None
        self.settings_overlay = None
        
        # Module registry for status tracking
        self.registered_modules = {}
    
    def initialize(self) -> bool:
        """Initialize the dashboard module"""
        try:
            self.logger.info("Initializing Dashboard module")
            
            # Initialize database connection
            self.db_manager = DatabaseManager()
            
            # Create the main screen
            self._create_dashboard_screen()
            
            self.logger.info("Dashboard module initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Dashboard module: {e}")
            return False
    
    def _create_dashboard_screen(self):
        """Create the main dashboard screen"""
        self.screen = Screen(name=self.module_id)
        
        # Apply theme background
        from kivy.graphics import Color, Rectangle
        with self.screen.canvas.before:
            Color(*StosOSTheme.get_color('background'))
            self.bg_rect = Rectangle(pos=self.screen.pos, size=self.screen.size)
        
        self.screen.bind(
            pos=lambda instance, value: setattr(self.bg_rect, 'pos', value),
            size=lambda instance, value: setattr(self.bg_rect, 'size', value)
        )
        
        # Main container
        main_container = BoxLayout(orientation='vertical')
        
        # Quick action bar
        action_bar = QuickActionBar(
            on_search=self._show_global_search,
            on_settings=self._show_settings,
            on_power=self._show_power_menu
        )
        main_container.add_widget(action_bar)
        
        # Dashboard content
        content_scroll = StosOSScrollView()
        content_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=StosOSTheme.get_spacing('lg'),
            spacing=StosOSTheme.get_spacing('lg')
        )
        content_container.bind(minimum_height=content_container.setter('height'))
        
        # Welcome section
        welcome_section = self._create_welcome_section()
        content_container.add_widget(welcome_section)
        
        # Module tiles grid
        modules_section = self._create_modules_section()
        content_container.add_widget(modules_section)
        
        # Quick stats section
        stats_section = self._create_stats_section()
        content_container.add_widget(stats_section)
        
        content_scroll.add_widget(content_container)
        main_container.add_widget(content_scroll)
        
        self.screen.add_widget(main_container)
    
    def _create_welcome_section(self) -> StosOSPanel:
        """Create welcome section with time and greeting"""
        section = StosOSPanel(
            size_hint_y=None,
            height=dp(100)
        )
        
        container = BoxLayout(
            orientation='vertical',
            padding=StosOSTheme.get_spacing('md'),
            spacing=StosOSTheme.get_spacing('sm')
        )
        
        # Greeting
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Good Morning"
        elif current_hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"
        
        greeting_label = StosOSLabel(
            text=f"{greeting}!",
            font_size=str(StosOSTheme.get_font_size('display')) + 'sp',
            color=StosOSTheme.get_color('accent_primary'),
            size_hint_y=None,
            height=dp(40),
            halign='center'
        )
        greeting_label.bind(size=greeting_label.setter('text_size'))
        container.add_widget(greeting_label)
        
        # Current date and time
        now = datetime.now()
        datetime_label = StosOSLabel(
            text=now.strftime('%A, %B %d, %Y • %H:%M'),
            font_size=str(StosOSTheme.get_font_size('body')) + 'sp',
            color=StosOSTheme.get_color('text_secondary'),
            size_hint_y=None,
            height=dp(30),
            halign='center'
        )
        datetime_label.bind(size=datetime_label.setter('text_size'))
        container.add_widget(datetime_label)
        
        section.add_widget(container)
        return section
    
    def _create_modules_section(self) -> StosOSPanel:
        """Create modules section with tiles"""
        section = StosOSPanel(
            title="Modules",
            size_hint_y=None,
            height=dp(400)
        )
        
        # Module tiles grid
        tiles_grid = GridLayout(
            cols=3,
            spacing=StosOSTheme.get_spacing('md'),
            padding=StosOSTheme.get_spacing('md'),
            size_hint_y=None
        )
        tiles_grid.bind(minimum_height=tiles_grid.setter('height'))
        
        # Define available modules
        modules_info = [
            {
                'module_id': 'task_manager',
                'display_name': 'Tasks',
                'description': 'Manage your tasks and deadlines',
                'icon': '✓',
                'status': {'connected': True, 'notifications': 3}
            },
            {
                'module_id': 'calendar_module',
                'display_name': 'Calendar',
                'description': 'View and manage events',
                'icon': '📅',
                'status': {'connected': True, 'notifications': 1}
            },
            {
                'module_id': 'idea_board',
                'display_name': 'Ideas',
                'description': 'Capture and organize ideas',
                'icon': '💡',
                'status': {'connected': True, 'notifications': 0}
            },
            {
                'module_id': 'study_tracker',
                'display_name': 'Study',
                'description': 'Track study sessions',
                'icon': '📚',
                'status': {'connected': True, 'notifications': 0}
            },
            {
                'module_id': 'smart_home',
                'display_name': 'Smart Home',
                'description': 'Control connected devices',
                'icon': '🏠',
                'status': {'connected': False, 'notifications': 0}
            },
            {
                'module_id': 'spotify_controller',
                'display_name': 'Music',
                'description': 'Control Spotify playback',
                'icon': '🎵',
                'status': {'connected': False, 'notifications': 0}
            }
        ]
        
        # Create tiles
        for module_info in modules_info:
            tile = ModuleTile(
                module_info=module_info,
                on_click=self._navigate_to_module
            )
            tiles_grid.add_widget(tile)
            
            # Store module info for status updates
            self.registered_modules[module_info['module_id']] = module_info
        
        section.add_widget(tiles_grid)
        return section
    
    def _create_stats_section(self) -> StosOSPanel:
        """Create quick stats section"""
        section = StosOSPanel(
            title="Quick Stats",
            size_hint_y=None,
            height=dp(150)
        )
        
        stats_grid = GridLayout(
            cols=3,
            spacing=StosOSTheme.get_spacing('md'),
            padding=StosOSTheme.get_spacing('md')
        )
        
        # Mock stats - in real implementation, these would come from modules
        stats = [
            ("Tasks Due", "5", "📋"),
            ("Study Hours", "2.5", "⏱️"),
            ("Ideas Captured", "12", "💭")
        ]
        
        for stat_name, stat_value, stat_icon in stats:
            stat_card = StosOSCard(size_hint_y=None, height=dp(80))
            
            stat_container = BoxLayout(
                orientation='vertical',
                padding=StosOSTheme.get_spacing('sm'),
                spacing=StosOSTheme.get_spacing('xs')
            )
            
            # Icon and value
            value_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=StosOSTheme.get_spacing('sm')
            )
            
            icon_label = StosOSLabel(
                text=stat_icon,
                font_size='20sp',
                size_hint_x=None,
                width=dp(30),
                halign='center'
            )
            value_container.add_widget(icon_label)
            
            value_label = StosOSLabel(
                text=stat_value,
                font_size=str(StosOSTheme.get_font_size('title')) + 'sp',
                color=StosOSTheme.get_color('accent_primary'),
                halign='left'
            )
            value_label.bind(size=value_label.setter('text_size'))
            value_container.add_widget(value_label)
            
            stat_container.add_widget(value_container)
            
            # Stat name
            name_label = StosOSLabel(
                text=stat_name,
                font_size=str(StosOSTheme.get_font_size('caption')) + 'sp',
                color=StosOSTheme.get_color('text_secondary'),
                size_hint_y=None,
                height=dp(20),
                halign='center'
            )
            name_label.bind(size=name_label.setter('text_size'))
            stat_container.add_widget(name_label)
            
            stat_card.add_widget(stat_container)
            stats_grid.add_widget(stat_card)
        
        section.add_widget(stats_grid)
        return section
    
    def _navigate_to_module(self, module_info: Dict[str, Any]):
        """Navigate to a specific module"""
        module_id = module_info['module_id']
        self.logger.info(f"Navigating to module: {module_id}")
        
        # Get screen manager from parent app
        if hasattr(self, '_screen_manager') and self._screen_manager:
            success = self._screen_manager.navigate_to_module(
                module_id, 
                transition_type='slide',
                direction='left'
            )
            if not success:
                self.logger.warning(f"Failed to navigate to module: {module_id}")
        else:
            self.logger.warning("Screen manager not available for navigation")
    
    def _show_global_search(self):
        """Show global search overlay"""
        if not self.search_overlay:
            self.search_overlay = GlobalSearchOverlay(
                on_close=self._hide_global_search,
                on_result_select=self._handle_search_result
            )
        
        # Add to screen
        self.screen.add_widget(self.search_overlay)
        StosOSAnimations.fade_in(self.search_overlay, duration=0.3)
    
    def _hide_global_search(self):
        """Hide global search overlay"""
        if self.search_overlay and self.search_overlay.parent:
            StosOSAnimations.fade_out(
                self.search_overlay, 
                duration=0.2,
                callback=lambda: self.screen.remove_widget(self.search_overlay)
            )
    
    def _handle_search_result(self, result: Dict[str, Any]):
        """Handle search result selection"""
        module_id = result.get('module_id')
        if module_id:
            # Navigate to the module containing the result
            self._navigate_to_module({'module_id': module_id})
    
    def _show_settings(self):
        """Show settings panel"""
        if not self.settings_overlay:
            # Get config manager from parent app
            config_manager = getattr(self, '_config_manager', None)
            if not config_manager:
                self.logger.warning("Config manager not available")
                return
            
            self.settings_overlay = FloatLayout()
            
            settings_panel = SettingsPanel(
                config_manager=config_manager,
                on_close=self._hide_settings,
                size_hint=(0.9, 0.9),
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            
            self.settings_overlay.add_widget(settings_panel)
        
        # Add to screen
        self.screen.add_widget(self.settings_overlay)
        StosOSAnimations.slide_in_from_right(self.settings_overlay, duration=0.3)
    
    def _hide_settings(self):
        """Hide settings panel"""
        if self.settings_overlay and self.settings_overlay.parent:
            StosOSAnimations.slide_out_to_right(
                self.settings_overlay,
                duration=0.2,
                callback=lambda: self.screen.remove_widget(self.settings_overlay)
            )
    
    def _show_power_menu(self):
        """Show power management menu"""
        # Create power menu popup
        power_menu = StosOSPopup(
            title="Power Options",
            size_hint=(0.6, 0.4)
        )
        
        content = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('md')
        )
        
        # Power options
        options = [
            ("Sleep Display", self._sleep_display),
            ("Restart System", self._restart_system),
            ("Shutdown System", self._shutdown_system)
        ]
        
        for option_text, option_callback in options:
            btn = StosOSButton(
                text=option_text,
                size_hint_y=None,
                height=dp(50)
            )
            btn.bind(on_press=lambda x, cb=option_callback: (power_menu.dismiss(), cb()))
            content.add_widget(btn)
        
        # Cancel button
        cancel_btn = StosOSButton(
            text="Cancel",
            size_hint_y=None,
            height=dp(50),
            button_type='secondary'
        )
        cancel_btn.bind(on_press=lambda x: power_menu.dismiss())
        content.add_widget(cancel_btn)
        
        power_menu.content = content
        power_menu.open_with_animation()
    
    def _sleep_display(self):
        """Sleep the display"""
        self.logger.info("Sleeping display")
        # In real implementation, this would trigger power manager
    
    def _restart_system(self):
        """Restart the system"""
        self.logger.info("Restarting system")
        # In real implementation, this would restart the Pi
    
    def _shutdown_system(self):
        """Shutdown the system"""
        self.logger.info("Shutting down system")
        # In real implementation, this would shutdown the Pi
    
    def get_screen(self) -> Screen:
        """Get the module screen"""
        return self.screen
    
    def on_activate(self):
        """Called when module becomes active"""
        self.logger.debug("Dashboard module activated")
        # Refresh module statuses
        self._refresh_module_statuses()
    
    def on_deactivate(self):
        """Called when module becomes inactive"""
        self.logger.debug("Dashboard module deactivated")
    
    def _refresh_module_statuses(self):
        """Refresh the status of all registered modules"""
        # In a real implementation, this would query actual module statuses
        # For now, we'll just update the display
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get module status"""
        return {
            'active': True,
            'modules_count': len(self.registered_modules),
            'last_updated': datetime.now().isoformat()
        }
    
    def cleanup(self):
        """Cleanup module resources"""
        self.logger.info("Cleaning up Dashboard module")
        
        # Close any open overlays
        if self.search_overlay and self.search_overlay.parent:
            self.screen.remove_widget(self.search_overlay)
        
        if self.settings_overlay and self.settings_overlay.parent:
            self.screen.remove_widget(self.settings_overlay)
        
        # Cancel any scheduled events
        Clock.unschedule(self._refresh_module_statuses)
        
        super().cleanup()