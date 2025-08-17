"""
Calendar Integration Module for StosOS

Provides Google Calendar integration with OAuth authentication, calendar display UI
with day, week, and month views, event creation and editing functionality,
unified timeline view combining calendar events and tasks, and calendar event
notifications and reminders.

Requirements: 2.1, 2.3
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional, Callable
from calendar import monthrange
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.metrics import dp

from core.base_module import BaseModule
from core.database_manager import DatabaseManager
from models.calendar_event import CalendarEvent
from models.task import Task
from services.google_calendar_service import GoogleCalendarService
from ui.components import (
    StosOSButton, StosOSLabel, StosOSTextInput, StosOSPanel, 
    StosOSCard, StosOSScrollView, StosOSPopup, StosOSLoadingOverlay,
    StosOSIconButton, StosOSToggleButton
)
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations


class CalendarEventCard(StosOSCard):
    """Individual calendar event card component"""
    
    def __init__(self, event: CalendarEvent, on_edit: Callable = None, 
                 on_delete: Callable = None, **kwargs):
        super().__init__(**kwargs)
        
        self.event = event
        self.on_edit = on_edit
        self.on_delete = on_delete
        
        self.size_hint_y = None
        self.height = dp(100)
        self.spacing = StosOSTheme.get_spacing('sm')
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the event card UI"""
        content_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        # Left side - event info
        info_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('xs'))
        
        # Title and time
        title_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
        
        # Event title
        title_label = StosOSLabel(
            text=self.event.title,
            label_type="title",
            color=StosOSTheme.get_color('text_primary'),
            size_hint_x=0.7
        )
        title_label.bind(size=title_label.setter('text_size'))
        title_layout.add_widget(title_label)
        
        # Status indicator
        status_color = self._get_status_color()
        status_label = StosOSLabel(
            text=self._get_status_text(),
            color=status_color,
            size_hint_x=0.3,
            halign='right',
            font_size=StosOSTheme.get_font_size('caption')
        )
        status_label.bind(size=status_label.setter('text_size'))
        title_layout.add_widget(status_label)
        
        info_layout.add_widget(title_layout)
        
        # Time display
        time_label = StosOSLabel(
            text=self.event.get_display_time(),
            color=StosOSTheme.get_color('accent_secondary'),
            font_size=StosOSTheme.get_font_size('body'),
            size_hint_y=None,
            height=dp(20)
        )
        info_layout.add_widget(time_label)
        
        # Location and description
        if self.event.location or self.event.description:
            details_text = ""
            if self.event.location:
                details_text += f"📍 {self.event.location}"
            if self.event.description:
                if details_text:
                    details_text += " • "
                details_text += self.event.description[:50]
                if len(self.event.description) > 50:
                    details_text += "..."
            
            details_label = StosOSLabel(
                text=details_text,
                color=StosOSTheme.get_color('text_secondary'),
                font_size=StosOSTheme.get_font_size('caption'),
                size_hint_y=None,
                height=dp(20)
            )
            details_label.bind(size=details_label.setter('text_size'))
            info_layout.add_widget(details_label)
        
        content_layout.add_widget(info_layout)
        
        # Right side - action buttons
        actions_layout = BoxLayout(
            orientation='vertical', 
            size_hint_x=None, 
            width=dp(60),
            spacing=StosOSTheme.get_spacing('xs')
        )
        
        # Edit button
        edit_btn = StosOSIconButton(
            icon="✏",
            size=(dp(30), dp(30)),
            button_type="secondary"
        )
        edit_btn.bind(on_press=self._on_edit)
        actions_layout.add_widget(edit_btn)
        
        # Delete button (only for local events)
        if self.event.is_local_only:
            delete_btn = StosOSIconButton(
                icon="🗑",
                size=(dp(30), dp(30)),
                button_type="danger"
            )
            delete_btn.bind(on_press=self._on_delete)
            actions_layout.add_widget(delete_btn)
        
        content_layout.add_widget(actions_layout)
        
        self.add_widget(content_layout)
    
    def _get_status_color(self):
        """Get color for status indicator"""
        if self.event.is_current:
            return StosOSTheme.get_color('success')
        elif self.event.is_upcoming:
            return StosOSTheme.get_color('info')
        else:
            return StosOSTheme.get_color('text_disabled')
    
    def _get_status_text(self):
        """Get status text"""
        if self.event.is_current:
            return "Now"
        elif self.event.is_upcoming:
            time_until = self.event.get_time_until_start()
            if time_until:
                if time_until.days > 0:
                    return f"{time_until.days}d"
                elif time_until.seconds > 3600:
                    hours = time_until.seconds // 3600
                    return f"{hours}h"
                else:
                    minutes = time_until.seconds // 60
                    return f"{minutes}m"
            return "Soon"
        else:
            return "Past"
    
    def _on_edit(self, *args):
        """Handle edit button press"""
        if self.on_edit:
            self.on_edit(self.event)
    
    def _on_delete(self, *args):
        """Handle delete button press"""
        if self.on_delete:
            self.on_delete(self.event)


class EventFormPopup(StosOSPopup):
    """Popup for creating/editing calendar events"""
    
    def __init__(self, event: CalendarEvent = None, on_save: Callable = None, **kwargs):
        self.event = event
        self.on_save = on_save
        self.is_editing = event is not None
        
        title = "Edit Event" if self.is_editing else "New Event"
        super().__init__(
            title=title,
            size_hint=(0.8, 0.8),
            auto_dismiss=False,
            **kwargs
        )
        
        self._build_form()
    
    def _build_form(self):
        """Build the event form"""
        form_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Title input
        self.title_input = StosOSTextInput(
            placeholder="Event title",
            text=self.event.title if self.is_editing else "",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        form_layout.add_widget(StosOSLabel(text="Title:", size_hint_y=None, height=dp(25)))
        form_layout.add_widget(self.title_input)
        
        # Description input
        self.description_input = StosOSTextInput(
            placeholder="Event description (optional)",
            text=self.event.description if self.is_editing else "",
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        form_layout.add_widget(StosOSLabel(text="Description:", size_hint_y=None, height=dp(25)))
        form_layout.add_widget(self.description_input)
        
        # Location input
        self.location_input = StosOSTextInput(
            placeholder="Location (optional)",
            text=self.event.location if self.is_editing else "",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        form_layout.add_widget(StosOSLabel(text="Location:", size_hint_y=None, height=dp(25)))
        form_layout.add_widget(self.location_input)
        
        # Date and time inputs
        datetime_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'),
                                   size_hint_y=None, height=StosOSTheme.get_dimension('input_height'))
        
        # Start date/time
        start_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        start_layout.add_widget(StosOSLabel(text="Start:", size_hint_y=None, height=dp(25)))
        
        self.start_date_input = StosOSTextInput(
            placeholder="YYYY-MM-DD",
            text=self.event.start_time.strftime('%Y-%m-%d') if self.is_editing and self.event.start_time else ""
        )
        start_layout.add_widget(self.start_date_input)
        
        self.start_time_input = StosOSTextInput(
            placeholder="HH:MM",
            text=self.event.start_time.strftime('%H:%M') if self.is_editing and self.event.start_time and not self.event.all_day else ""
        )
        start_layout.add_widget(self.start_time_input)
        
        datetime_layout.add_widget(start_layout)
        
        # End date/time
        end_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        end_layout.add_widget(StosOSLabel(text="End:", size_hint_y=None, height=dp(25)))
        
        self.end_date_input = StosOSTextInput(
            placeholder="YYYY-MM-DD",
            text=self.event.end_time.strftime('%Y-%m-%d') if self.is_editing and self.event.end_time else ""
        )
        end_layout.add_widget(self.end_date_input)
        
        self.end_time_input = StosOSTextInput(
            placeholder="HH:MM",
            text=self.event.end_time.strftime('%H:%M') if self.is_editing and self.event.end_time and not self.event.all_day else ""
        )
        end_layout.add_widget(self.end_time_input)
        
        datetime_layout.add_widget(end_layout)
        
        form_layout.add_widget(datetime_layout)
        
        # All day toggle
        self.all_day_toggle = StosOSToggleButton(
            text="All Day Event",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('button_height')
        )
        if self.is_editing:
            self.all_day_toggle.is_toggled = self.event.all_day
        self.all_day_toggle.bind(on_press=self._on_all_day_toggle)
        form_layout.add_widget(self.all_day_toggle)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'),
                                 size_hint_y=None, height=StosOSTheme.get_dimension('button_height'))
        
        cancel_btn = StosOSButton(
            text="Cancel",
            button_type="secondary",
            size_hint_x=0.5
        )
        cancel_btn.bind(on_press=self.dismiss)
        button_layout.add_widget(cancel_btn)
        
        save_btn = StosOSButton(
            text="Save",
            button_type="accent",
            size_hint_x=0.5
        )
        save_btn.bind(on_press=self._save_event)
        button_layout.add_widget(save_btn)
        
        form_layout.add_widget(button_layout)
        
        self.content = form_layout
    
    def _on_all_day_toggle(self, *args):
        """Handle all day toggle"""
        if self.all_day_toggle.is_toggled:
            self.start_time_input.disabled = True
            self.end_time_input.disabled = True
            self.start_time_input.text = ""
            self.end_time_input.text = ""
        else:
            self.start_time_input.disabled = False
            self.end_time_input.disabled = False
    
    def _save_event(self, *args):
        """Save the event"""
        try:
            # Validate title
            title = self.title_input.text.strip()
            if not title:
                return
            
            # Parse dates
            start_date = None
            end_date = None
            
            if self.start_date_input.text.strip():
                start_date = datetime.strptime(self.start_date_input.text.strip(), '%Y-%m-%d').date()
            
            if self.end_date_input.text.strip():
                end_date = datetime.strptime(self.end_date_input.text.strip(), '%Y-%m-%d').date()
            
            # Parse times if not all day
            start_time = None
            end_time = None
            
            if not self.all_day_toggle.is_toggled:
                if self.start_time_input.text.strip():
                    start_time_obj = datetime.strptime(self.start_time_input.text.strip(), '%H:%M').time()
                    if start_date:
                        start_time = datetime.combine(start_date, start_time_obj)
                
                if self.end_time_input.text.strip():
                    end_time_obj = datetime.strptime(self.end_time_input.text.strip(), '%H:%M').time()
                    if end_date:
                        end_time = datetime.combine(end_date, end_time_obj)
            else:
                # All day event
                if start_date:
                    start_time = datetime.combine(start_date, datetime.min.time())
                if end_date:
                    end_time = datetime.combine(end_date, datetime.min.time())
            
            # Create or update event
            if self.is_editing:
                self.event.title = title
                self.event.description = self.description_input.text.strip()
                self.event.location = self.location_input.text.strip()
                self.event.start_time = start_time
                self.event.end_time = end_time
                self.event.all_day = self.all_day_toggle.is_toggled
                self.event.updated_at = datetime.now()
                self.event.needs_sync = True
            else:
                self.event = CalendarEvent(
                    title=title,
                    description=self.description_input.text.strip(),
                    location=self.location_input.text.strip(),
                    start_time=start_time,
                    end_time=end_time,
                    all_day=self.all_day_toggle.is_toggled,
                    is_local_only=True,
                    needs_sync=True
                )
            
            # Call save callback
            if self.on_save:
                self.on_save(self.event)
            
            self.dismiss()
            
        except Exception as e:
            logging.error(f"Error saving event: {e}")


class CalendarModule(BaseModule):
    """
    Calendar Integration Module
    
    Provides Google Calendar integration with OAuth authentication, calendar display UI
    with day, week, and month views, event creation and editing functionality,
    unified timeline view combining calendar events and tasks, and calendar event
    notifications and reminders.
    """
    
    def __init__(self):
        super().__init__(
            module_id="calendar",
            display_name="Calendar",
            icon="📅"
        )
        
        self.db_manager = None
        self.google_service = None
        self.events = []
        self.tasks = []
        self.current_view = "week"  # day, week, month, timeline
        self.current_date = datetime.now().date()
        
        # UI components
        self.event_list_layout = None
        self.view_buttons = {}
        self.date_navigation = None
        
        # Sync tracking
        self.last_sync = None
        self.sync_timer = None
    
    def initialize(self) -> bool:
        """Initialize the calendar module"""
        try:
            self.db_manager = DatabaseManager()
            self.google_service = GoogleCalendarService()
            
            # Try to authenticate with Google Calendar
            if self.google_service.authenticate():
                self.logger.info("Google Calendar authentication successful")
            else:
                self.logger.warning("Google Calendar authentication failed - running in offline mode")
            
            self._load_events()
            self._load_tasks()
            self._start_sync_timer()
            
            self._initialized = True
            self.logger.info("Calendar module initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Calendar module: {e}")
            self.handle_error(e, "initialization")
            return False
    
    def get_screen(self) -> Screen:
        """Get the calendar screen"""
        if self.screen_widget is None:
            self.screen_widget = Screen(name=self.module_id)
            self._build_ui()
        return self.screen_widget
    
    def _build_ui(self):
        """Build the calendar UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Header with title and sync button
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        title_label = StosOSLabel(
            text="📅 Calendar",
            label_type="title",
            size_hint_x=0.5
        )
        header_layout.add_widget(title_label)
        
        # Sync status
        self.sync_status_label = StosOSLabel(
            text="Offline",
            color=StosOSTheme.get_color('text_secondary'),
            size_hint_x=0.3
        )
        header_layout.add_widget(self.sync_status_label)
        
        # Add event button
        add_btn = StosOSButton(
            text="+ Event",
            button_type="accent",
            size_hint_x=0.2
        )
        add_btn.bind(on_press=self._show_new_event_form)
        header_layout.add_widget(add_btn)
        
        main_layout.add_widget(header_layout)
        
        # View selection and date navigation
        self._build_navigation_panel()
        main_layout.add_widget(self.navigation_panel)
        
        # Calendar view area
        self._build_calendar_view()
        main_layout.add_widget(self.calendar_view_layout)
        
        self.screen_widget.add_widget(main_layout)
        
        # Update sync status
        self._update_sync_status()
    
    def _build_navigation_panel(self):
        """Build the navigation and view selection panel"""
        self.navigation_panel = StosOSPanel(
            title="Navigation",
            size_hint_y=None,
            height=dp(120)
        )
        
        nav_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # View selection buttons
        view_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('xs'))
        
        views = [
            ("day", "Day"),
            ("week", "Week"), 
            ("month", "Month"),
            ("timeline", "Timeline")
        ]
        
        for view_id, view_name in views:
            btn = StosOSToggleButton(
                text=view_name,
                button_type="accent" if view_id == self.current_view else "secondary"
            )
            btn.bind(on_press=lambda x, v=view_id: self._change_view(v))
            self.view_buttons[view_id] = btn
            view_layout.add_widget(btn)
        
        nav_layout.add_widget(view_layout)
        
        # Date navigation
        date_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        prev_btn = StosOSIconButton(
            icon="◀",
            size=(dp(40), dp(40)),
            button_type="secondary"
        )
        prev_btn.bind(on_press=self._navigate_previous)
        date_layout.add_widget(prev_btn)
        
        self.date_label = StosOSLabel(
            text=self._get_date_display(),
            halign='center',
            label_type="title"
        )
        date_layout.add_widget(self.date_label)
        
        next_btn = StosOSIconButton(
            icon="▶",
            size=(dp(40), dp(40)),
            button_type="secondary"
        )
        next_btn.bind(on_press=self._navigate_next)
        date_layout.add_widget(next_btn)
        
        today_btn = StosOSButton(
            text="Today",
            button_type="accent",
            size_hint_x=None,
            width=dp(80)
        )
        today_btn.bind(on_press=self._navigate_today)
        date_layout.add_widget(today_btn)
        
        nav_layout.add_widget(date_layout)
        
        self.navigation_panel.add_widget(nav_layout)
    
    def _build_calendar_view(self):
        """Build the calendar view area"""
        self.calendar_view_layout = StosOSScrollView()
        
        self.calendar_container = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('sm'),
            size_hint_y=None
        )
        self.calendar_container.bind(minimum_height=self.calendar_container.setter('height'))
        
        self.calendar_view_layout.add_widget(self.calendar_container)
        
        # Initial view
        self._refresh_calendar_view()
    
    def _load_events(self):
        """Load events from database"""
        try:
            self.events = self.db_manager.get_calendar_events()
            self.logger.debug(f"Loaded {len(self.events)} events from database")
        except Exception as e:
            self.logger.error(f"Failed to load events: {e}")
            self.events = []
    
    def _load_tasks(self):
        """Load tasks from database for timeline view"""
        try:
            self.tasks = self.db_manager.get_tasks()
            self.logger.debug(f"Loaded {len(self.tasks)} tasks for timeline")
        except Exception as e:
            self.logger.error(f"Failed to load tasks: {e}")
            self.tasks = []
    
    def _start_sync_timer(self):
        """Start automatic sync timer"""
        if self.sync_timer:
            self.sync_timer.cancel()
        
        # Sync every 5 minutes if authenticated
        if self.google_service.is_authenticated():
            self.sync_timer = Clock.schedule_interval(self._sync_with_google, 300)
    
    def _sync_with_google(self, *args):
        """Sync events with Google Calendar"""
        if not self.google_service.is_authenticated():
            return
        
        try:
            # Get events from Google Calendar
            google_events = self.google_service.get_events()
            
            # Update local database
            for google_event in google_events:
                existing_event = self.db_manager.get_calendar_event_by_google_id(google_event.google_event_id)
                if existing_event:
                    # Update existing event
                    google_event.id = existing_event.id
                    self.db_manager.update_calendar_event(google_event)
                else:
                    # Create new event
                    self.db_manager.create_calendar_event(google_event)
            
            # Sync local changes to Google
            local_events_needing_sync = self.db_manager.get_calendar_events(needs_sync=True)
            if local_events_needing_sync:
                updated_events, errors = self.google_service.sync_events(local_events_needing_sync)
                
                # Update database with sync results
                for event in updated_events:
                    self.db_manager.update_calendar_event(event)
                
                if errors:
                    self.logger.warning(f"Sync errors: {errors}")
            
            self.last_sync = datetime.now()
            self._load_events()
            self._refresh_calendar_view()
            self._update_sync_status()
            
            self.logger.debug("Calendar sync completed successfully")
            
        except Exception as e:
            self.logger.error(f"Calendar sync failed: {e}")
    
    def _update_sync_status(self):
        """Update sync status display"""
        if hasattr(self, 'sync_status_label'):
            if self.google_service.is_authenticated():
                if self.last_sync:
                    time_diff = datetime.now() - self.last_sync
                    if time_diff.total_seconds() < 300:  # Less than 5 minutes
                        self.sync_status_label.text = "✓ Synced"
                        self.sync_status_label.color = StosOSTheme.get_color('success')
                    else:
                        self.sync_status_label.text = "⚠ Sync pending"
                        self.sync_status_label.color = StosOSTheme.get_color('warning')
                else:
                    self.sync_status_label.text = "🔄 Syncing..."
                    self.sync_status_label.color = StosOSTheme.get_color('info')
            else:
                self.sync_status_label.text = "📴 Offline"
                self.sync_status_label.color = StosOSTheme.get_color('text_disabled')
    
    def _change_view(self, view_id: str):
        """Change calendar view"""
        self.current_view = view_id
        
        # Update button states
        for vid, btn in self.view_buttons.items():
            btn.button_type = "accent" if vid == view_id else "secondary"
            btn._update_appearance()
        
        self._refresh_calendar_view()
    
    def _navigate_previous(self, *args):
        """Navigate to previous period"""
        if self.current_view == "day":
            self.current_date -= timedelta(days=1)
        elif self.current_view == "week":
            self.current_date -= timedelta(weeks=1)
        elif self.current_view == "month":
            # Go to previous month
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        
        self.date_label.text = self._get_date_display()
        self._refresh_calendar_view()
    
    def _navigate_next(self, *args):
        """Navigate to next period"""
        if self.current_view == "day":
            self.current_date += timedelta(days=1)
        elif self.current_view == "week":
            self.current_date += timedelta(weeks=1)
        elif self.current_view == "month":
            # Go to next month
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        
        self.date_label.text = self._get_date_display()
        self._refresh_calendar_view()
    
    def _navigate_today(self, *args):
        """Navigate to today"""
        self.current_date = datetime.now().date()
        self.date_label.text = self._get_date_display()
        self._refresh_calendar_view()
    
    def _get_date_display(self) -> str:
        """Get formatted date display for current view"""
        if self.current_view == "day":
            return self.current_date.strftime('%A, %B %d, %Y')
        elif self.current_view == "week":
            # Get start of week (Monday)
            start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            return f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d, %Y')}"
        elif self.current_view == "month":
            return self.current_date.strftime('%B %Y')
        else:  # timeline
            return "Timeline View"
    
    def _refresh_calendar_view(self):
        """Refresh the calendar view based on current view mode"""
        self.calendar_container.clear_widgets()
        
        if self.current_view == "day":
            self._build_day_view()
        elif self.current_view == "week":
            self._build_week_view()
        elif self.current_view == "month":
            self._build_month_view()
        elif self.current_view == "timeline":
            self._build_timeline_view()
    
    def _build_day_view(self):
        """Build day view"""
        # Get events for the current day
        start_of_day = datetime.combine(self.current_date, datetime.min.time())
        end_of_day = datetime.combine(self.current_date, datetime.max.time())
        
        day_events = [
            event for event in self.events
            if event.start_time and start_of_day <= event.start_time <= end_of_day
        ]
        
        day_events.sort(key=lambda e: e.start_time or datetime.min)
        
        if day_events:
            for event in day_events:
                event_card = CalendarEventCard(
                    event=event,
                    on_edit=self._edit_event,
                    on_delete=self._delete_event
                )
                self.calendar_container.add_widget(event_card)
        else:
            empty_label = StosOSLabel(
                text="No events for this day",
                halign='center',
                color=StosOSTheme.get_color('text_disabled'),
                size_hint_y=None,
                height=dp(100)
            )
            self.calendar_container.add_widget(empty_label)
    
    def _build_week_view(self):
        """Build week view"""
        # Get start of week (Monday)
        start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        start_datetime = datetime.combine(start_of_week, datetime.min.time())
        end_datetime = datetime.combine(end_of_week, datetime.max.time())
        
        week_events = [
            event for event in self.events
            if event.start_time and start_datetime <= event.start_time <= end_datetime
        ]
        
        # Group events by day
        for i in range(7):
            day_date = start_of_week + timedelta(days=i)
            day_start = datetime.combine(day_date, datetime.min.time())
            day_end = datetime.combine(day_date, datetime.max.time())
            
            day_events = [
                event for event in week_events
                if event.start_time and day_start <= event.start_time <= day_end
            ]
            
            # Day header
            day_header = StosOSLabel(
                text=day_date.strftime('%A, %b %d'),
                label_type="subtitle",
                size_hint_y=None,
                height=dp(30)
            )
            self.calendar_container.add_widget(day_header)
            
            # Day events
            if day_events:
                for event in sorted(day_events, key=lambda e: e.start_time or datetime.min):
                    event_card = CalendarEventCard(
                        event=event,
                        on_edit=self._edit_event,
                        on_delete=self._delete_event
                    )
                    self.calendar_container.add_widget(event_card)
            else:
                empty_label = StosOSLabel(
                    text="No events",
                    color=StosOSTheme.get_color('text_disabled'),
                    size_hint_y=None,
                    height=dp(40)
                )
                self.calendar_container.add_widget(empty_label)
    
    def _build_month_view(self):
        """Build month view"""
        # Get first and last day of month
        first_day = self.current_date.replace(day=1)
        last_day_num = monthrange(self.current_date.year, self.current_date.month)[1]
        last_day = self.current_date.replace(day=last_day_num)
        
        start_datetime = datetime.combine(first_day, datetime.min.time())
        end_datetime = datetime.combine(last_day, datetime.max.time())
        
        month_events = [
            event for event in self.events
            if event.start_time and start_datetime <= event.start_time <= end_datetime
        ]
        
        # Group events by date
        events_by_date = {}
        for event in month_events:
            event_date = event.start_time.date()
            if event_date not in events_by_date:
                events_by_date[event_date] = []
            events_by_date[event_date].append(event)
        
        # Create calendar grid (simplified version)
        current_day = first_day
        while current_day <= last_day:
            day_events = events_by_date.get(current_day, [])
            
            # Day header
            day_header = StosOSLabel(
                text=current_day.strftime('%d - %A'),
                label_type="subtitle",
                size_hint_y=None,
                height=dp(30)
            )
            self.calendar_container.add_widget(day_header)
            
            # Day events (show first 3)
            if day_events:
                for event in day_events[:3]:
                    event_card = CalendarEventCard(
                        event=event,
                        on_edit=self._edit_event,
                        on_delete=self._delete_event
                    )
                    self.calendar_container.add_widget(event_card)
                
                if len(day_events) > 3:
                    more_label = StosOSLabel(
                        text=f"... and {len(day_events) - 3} more",
                        color=StosOSTheme.get_color('text_secondary'),
                        size_hint_y=None,
                        height=dp(20)
                    )
                    self.calendar_container.add_widget(more_label)
            
            current_day += timedelta(days=1)
    
    def _build_timeline_view(self):
        """Build unified timeline view with events and tasks"""
        # Combine events and tasks
        timeline_items = []
        
        # Add events
        for event in self.events:
            if event.start_time:
                timeline_items.append({
                    'type': 'event',
                    'item': event,
                    'datetime': event.start_time,
                    'title': event.title
                })
        
        # Add tasks with due dates
        for task in self.tasks:
            if task.due_date:
                timeline_items.append({
                    'type': 'task',
                    'item': task,
                    'datetime': task.due_date,
                    'title': task.title
                })
        
        # Sort by datetime
        timeline_items.sort(key=lambda x: x['datetime'])
        
        # Group by date
        current_date = None
        for item in timeline_items:
            item_date = item['datetime'].date()
            
            # Add date header if new date
            if current_date != item_date:
                current_date = item_date
                date_header = StosOSLabel(
                    text=item_date.strftime('%A, %B %d, %Y'),
                    label_type="title",
                    size_hint_y=None,
                    height=dp(40)
                )
                self.calendar_container.add_widget(date_header)
            
            # Add item
            if item['type'] == 'event':
                event_card = CalendarEventCard(
                    event=item['item'],
                    on_edit=self._edit_event,
                    on_delete=self._delete_event
                )
                self.calendar_container.add_widget(event_card)
            else:  # task
                # Create a simple task display
                task_layout = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(50),
                    spacing=StosOSTheme.get_spacing('md')
                )
                
                task_icon = StosOSLabel(
                    text="📋",
                    size_hint_x=None,
                    width=dp(30)
                )
                task_layout.add_widget(task_icon)
                
                task_info = BoxLayout(orientation='vertical')
                
                task_title = StosOSLabel(
                    text=item['item'].title,
                    label_type="body"
                )
                task_info.add_widget(task_title)
                
                task_time = StosOSLabel(
                    text=f"Due: {item['datetime'].strftime('%I:%M %p')}",
                    color=StosOSTheme.get_color('text_secondary'),
                    font_size=StosOSTheme.get_font_size('caption')
                )
                task_info.add_widget(task_time)
                
                task_layout.add_widget(task_info)
                
                self.calendar_container.add_widget(task_layout)
        
        if not timeline_items:
            empty_label = StosOSLabel(
                text="No events or tasks to display",
                halign='center',
                color=StosOSTheme.get_color('text_disabled'),
                size_hint_y=None,
                height=dp(100)
            )
            self.calendar_container.add_widget(empty_label)
    
    def _show_new_event_form(self, *args):
        """Show form for creating new event"""
        popup = EventFormPopup(on_save=self._save_new_event)
        popup.open_with_animation()
    
    def _save_new_event(self, event: CalendarEvent):
        """Save new event to database"""
        try:
            if self.db_manager.create_calendar_event(event):
                self.events.append(event)
                self._refresh_calendar_view()
                self.logger.info(f"Created new event: {event.title}")
                
                # Trigger sync if authenticated
                if self.google_service.is_authenticated():
                    Clock.schedule_once(lambda dt: self._sync_with_google(), 1)
            else:
                self.logger.error("Failed to save new event to database")
        except Exception as e:
            self.logger.error(f"Error saving new event: {e}")
            self.handle_error(e, "save_new_event")
    
    def _edit_event(self, event: CalendarEvent):
        """Show form for editing existing event"""
        popup = EventFormPopup(event=event, on_save=self._save_edited_event)
        popup.open_with_animation()
    
    def _save_edited_event(self, event: CalendarEvent):
        """Save edited event to database"""
        try:
            if self.db_manager.update_calendar_event(event):
                self._refresh_calendar_view()
                self.logger.info(f"Updated event: {event.title}")
                
                # Trigger sync if authenticated
                if self.google_service.is_authenticated():
                    Clock.schedule_once(lambda dt: self._sync_with_google(), 1)
            else:
                self.logger.error("Failed to update event in database")
        except Exception as e:
            self.logger.error(f"Error updating event: {e}")
            self.handle_error(e, "save_edited_event")
    
    def _delete_event(self, event: CalendarEvent):
        """Delete event with confirmation"""
        def confirm_delete():
            try:
                if self.db_manager.delete_calendar_event(event.id):
                    self.events = [e for e in self.events if e.id != event.id]
                    self._refresh_calendar_view()
                    self.logger.info(f"Deleted event: {event.title}")
                    
                    # Delete from Google Calendar if it exists there
                    if event.google_event_id and self.google_service.is_authenticated():
                        self.google_service.delete_event(event.google_event_id)
                else:
                    self.logger.error("Failed to delete event from database")
            except Exception as e:
                self.logger.error(f"Error deleting event: {e}")
                self.handle_error(e, "delete_event")
        
        # Show confirmation popup
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        message = StosOSLabel(
            text=f"Are you sure you want to delete '{event.title}'?",
            halign='center'
        )
        message.bind(size=message.setter('text_size'))
        content.add_widget(message)
        
        button_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        cancel_btn = StosOSButton(text="Cancel", button_type="secondary")
        delete_btn = StosOSButton(text="Delete", button_type="danger")
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(delete_btn)
        content.add_widget(button_layout)
        
        popup = StosOSPopup(
            title="Confirm Delete",
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        delete_btn.bind(on_press=lambda x: (confirm_delete(), popup.dismiss()))
        
        popup.open_with_animation()
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice commands for calendar"""
        command_lower = command.lower()
        
        if "calendar" in command_lower or "event" in command_lower:
            if "create" in command_lower or "add" in command_lower or "new" in command_lower:
                self._show_new_event_form()
                return True
            elif "today" in command_lower:
                self.current_view = "day"
                self.current_date = datetime.now().date()
                self._change_view("day")
                return True
            elif "week" in command_lower:
                self._change_view("week")
                return True
            elif "month" in command_lower:
                self._change_view("month")
                return True
            elif "timeline" in command_lower:
                self._change_view("timeline")
                return True
            elif "sync" in command_lower:
                self._sync_with_google()
                return True
        
        return False
    
    def cleanup(self):
        """Cleanup module resources"""
        if self.sync_timer:
            self.sync_timer.cancel()
        super().cleanup()