"""
Study Tracker Module for StosOS

Provides comprehensive study tracking and productivity features including:
- Time tracking and session management
- Pomodoro timer with 25-minute work sessions and break intervals
- Study statistics dashboard with daily/weekly analytics
- Goal setting and progress tracking for study targets
- Streak counter and motivational elements for sustained engagement

Requirements: 6.1, 6.2, 6.4, 6.5
"""

import logging
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional, Callable
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.animation import Animation

from core.base_module import BaseModule
from core.database_manager import DatabaseManager
from models.study_session import StudySession
from ui.components import (
    StosOSButton, StosOSLabel, StosOSTextInput, StosOSPanel, 
    StosOSCard, StosOSScrollView, StosOSPopup, StosOSLoadingOverlay,
    StosOSIconButton, StosOSToggleButton
)
from ui.theme import StosOSTheme
from ui.animations import StosOSAnimations


class PomodoroTimer:
    """Pomodoro timer implementation with work/break cycles"""
    
    def __init__(self, on_tick: Callable = None, on_complete: Callable = None):
        self.work_duration = 25 * 60  # 25 minutes in seconds
        self.short_break_duration = 5 * 60  # 5 minutes
        self.long_break_duration = 15 * 60  # 15 minutes
        
        self.current_time = 0
        self.is_running = False
        self.is_work_session = True
        self.session_count = 0
        
        self.on_tick = on_tick
        self.on_complete = on_complete
        
        self.timer_event = None
        
        self.reset()
    
    def reset(self):
        """Reset timer to initial state"""
        self.current_time = self.work_duration
        self.is_running = False
        self.is_work_session = True
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None
    
    def start(self):
        """Start the timer"""
        if not self.is_running:
            self.is_running = True
            self.timer_event = Clock.schedule_interval(self._tick, 1.0)
    
    def pause(self):
        """Pause the timer"""
        if self.is_running:
            self.is_running = False
            if self.timer_event:
                self.timer_event.cancel()
                self.timer_event = None
    
    def stop(self):
        """Stop and reset the timer"""
        self.pause()
        self.reset()
    
    def _tick(self, dt):
        """Timer tick callback"""
        if self.current_time > 0:
            self.current_time -= 1
            if self.on_tick:
                self.on_tick(self.current_time, self.is_work_session)
        else:
            # Timer completed
            self._complete_session()
    
    def _complete_session(self):
        """Handle session completion"""
        self.pause()
        
        if self.is_work_session:
            self.session_count += 1
            # Switch to break
            self.is_work_session = False
            if self.session_count % 4 == 0:
                # Long break after 4 work sessions
                self.current_time = self.long_break_duration
            else:
                # Short break
                self.current_time = self.short_break_duration
        else:
            # Break completed, switch to work
            self.is_work_session = True
            self.current_time = self.work_duration
        
        if self.on_complete:
            self.on_complete(self.is_work_session, self.session_count)
    
    def get_formatted_time(self) -> str:
        """Get formatted time string (MM:SS)"""
        minutes = self.current_time // 60
        seconds = self.current_time % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress(self) -> float:
        """Get progress as percentage (0.0 to 1.0)"""
        if self.is_work_session:
            total = self.work_duration
        elif self.session_count % 4 == 0:
            total = self.long_break_duration
        else:
            total = self.short_break_duration
        
        return 1.0 - (self.current_time / total)


class StudyGoal:
    """Study goal data structure"""
    
    def __init__(self, subject: str, daily_minutes: int, weekly_minutes: int = None):
        self.subject = subject
        self.daily_minutes = daily_minutes
        self.weekly_minutes = weekly_minutes or (daily_minutes * 7)
        self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            'subject': self.subject,
            'daily_minutes': self.daily_minutes,
            'weekly_minutes': self.weekly_minutes,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StudyGoal':
        """Create from dictionary"""
        goal = cls(data['subject'], data['daily_minutes'], data.get('weekly_minutes'))
        if data.get('created_at'):
            goal.created_at = datetime.fromisoformat(data['created_at'])
        return goal


class StudyStats:
    """Study statistics calculator"""
    
    def __init__(self, sessions: List[StudySession]):
        self.sessions = sessions
    
    def get_daily_stats(self, target_date: date = None) -> Dict[str, Any]:
        """Get statistics for a specific day"""
        if target_date is None:
            target_date = date.today()
        
        day_sessions = [
            s for s in self.sessions 
            if s.start_time.date() == target_date and s.end_time
        ]
        
        total_minutes = sum(s.duration for s in day_sessions)
        subject_breakdown = {}
        
        for session in day_sessions:
            if session.subject not in subject_breakdown:
                subject_breakdown[session.subject] = 0
            subject_breakdown[session.subject] += session.duration
        
        return {
            'date': target_date,
            'total_minutes': total_minutes,
            'session_count': len(day_sessions),
            'subject_breakdown': subject_breakdown,
            'sessions': day_sessions
        }
    
    def get_weekly_stats(self, week_start: date = None) -> Dict[str, Any]:
        """Get statistics for a week"""
        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        week_end = week_start + timedelta(days=6)
        
        week_sessions = [
            s for s in self.sessions 
            if week_start <= s.start_time.date() <= week_end and s.end_time
        ]
        
        total_minutes = sum(s.duration for s in week_sessions)
        daily_breakdown = {}
        subject_breakdown = {}
        
        # Initialize daily breakdown
        for i in range(7):
            day = week_start + timedelta(days=i)
            daily_breakdown[day] = 0
        
        for session in week_sessions:
            session_date = session.start_time.date()
            daily_breakdown[session_date] += session.duration
            
            if session.subject not in subject_breakdown:
                subject_breakdown[session.subject] = 0
            subject_breakdown[session.subject] += session.duration
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'total_minutes': total_minutes,
            'session_count': len(week_sessions),
            'daily_breakdown': daily_breakdown,
            'subject_breakdown': subject_breakdown,
            'average_daily_minutes': total_minutes / 7
        }
    
    def get_streak_count(self) -> int:
        """Calculate current study streak in days"""
        if not self.sessions:
            return 0
        
        # Get unique study dates, sorted in descending order
        study_dates = sorted(set(
            s.start_time.date() for s in self.sessions 
            if s.end_time and s.duration >= 15  # Minimum 15 minutes to count
        ), reverse=True)
        
        if not study_dates:
            return 0
        
        # Check if today has study time
        today = date.today()
        streak = 0
        
        # Start from today or the most recent study date
        current_date = today if today in study_dates else study_dates[0]
        
        for study_date in study_dates:
            if study_date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif study_date == current_date:
                # Continue streak
                streak += 1
                current_date -= timedelta(days=1)
            else:
                # Gap in streak
                break
        
        return streak
    
    def get_subject_progress(self, subject: str, days: int = 30) -> Dict[str, Any]:
        """Get progress for a specific subject over time"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        subject_sessions = [
            s for s in self.sessions 
            if s.subject == subject and start_date <= s.start_time.date() <= end_date and s.end_time
        ]
        
        total_minutes = sum(s.duration for s in subject_sessions)
        session_count = len(subject_sessions)
        
        # Daily breakdown
        daily_minutes = {}
        for i in range(days):
            day = start_date + timedelta(days=i)
            daily_minutes[day] = 0
        
        for session in subject_sessions:
            session_date = session.start_time.date()
            daily_minutes[session_date] += session.duration
        
        return {
            'subject': subject,
            'period_days': days,
            'total_minutes': total_minutes,
            'session_count': session_count,
            'average_daily_minutes': total_minutes / days,
            'daily_minutes': daily_minutes
        }


class PomodoroCard(StosOSCard):
    """Pomodoro timer card component"""
    
    def __init__(self, study_tracker, **kwargs):
        super().__init__(**kwargs)
        self.study_tracker = study_tracker
        self.timer = PomodoroTimer(
            on_tick=self._on_timer_tick,
            on_complete=self._on_timer_complete
        )
        
        self.size_hint_y = None
        self.height = dp(200)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the Pomodoro timer UI"""
        layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Title
        title_label = StosOSLabel(
            text="🍅 Pomodoro Timer",
            label_type="title",
            halign='center',
            size_hint_y=None,
            height=dp(30)
        )
        layout.add_widget(title_label)
        
        # Timer display
        self.timer_label = StosOSLabel(
            text=self.timer.get_formatted_time(),
            font_size=StosOSTheme.get_font_size('display'),
            halign='center',
            size_hint_y=None,
            height=dp(60)
        )
        layout.add_widget(self.timer_label)
        
        # Session type and count
        self.session_info_label = StosOSLabel(
            text="Work Session • Session 1",
            halign='center',
            color=StosOSTheme.get_color('accent_secondary'),
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(self.session_info_label)
        
        # Progress bar
        self.progress_bar = StosOSProgressBar(
            value=0,
            size_hint_y=None,
            height=dp(8)
        )
        layout.add_widget(self.progress_bar)
        
        # Control buttons
        button_layout = BoxLayout(
            orientation='horizontal',
            spacing=StosOSTheme.get_spacing('md'),
            size_hint_y=None,
            height=dp(40)
        )
        
        self.start_pause_btn = StosOSButton(
            text="Start",
            button_type="accent",
            size_hint_x=0.4
        )
        self.start_pause_btn.bind(on_press=self._toggle_timer)
        button_layout.add_widget(self.start_pause_btn)
        
        self.reset_btn = StosOSButton(
            text="Reset",
            button_type="secondary",
            size_hint_x=0.3
        )
        self.reset_btn.bind(on_press=self._reset_timer)
        button_layout.add_widget(self.reset_btn)
        
        self.skip_btn = StosOSButton(
            text="Skip",
            button_type="secondary",
            size_hint_x=0.3
        )
        self.skip_btn.bind(on_press=self._skip_session)
        button_layout.add_widget(self.skip_btn)
        
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    
    def _toggle_timer(self, *args):
        """Toggle timer start/pause"""
        if self.timer.is_running:
            self.timer.pause()
            self.start_pause_btn.text = "Start"
        else:
            self.timer.start()
            self.start_pause_btn.text = "Pause"
    
    def _reset_timer(self, *args):
        """Reset the timer"""
        self.timer.stop()
        self.start_pause_btn.text = "Start"
        self._update_display()
    
    def _skip_session(self, *args):
        """Skip current session"""
        self.timer._complete_session()
        self.start_pause_btn.text = "Start"
        self._update_display()
    
    def _on_timer_tick(self, remaining_time: int, is_work_session: bool):
        """Handle timer tick"""
        self._update_display()
    
    def _on_timer_complete(self, next_is_work: bool, session_count: int):
        """Handle timer completion"""
        self.start_pause_btn.text = "Start"
        self._update_display()
        
        # Show completion notification
        session_type = "Work" if not next_is_work else "Break"
        message = f"{session_type} session completed!"
        
        if not next_is_work and session_count % 4 == 0:
            message += " Time for a long break!"
        
        # Could show a popup or notification here
        self.study_tracker.logger.info(message)
    
    def _update_display(self):
        """Update timer display"""
        self.timer_label.text = self.timer.get_formatted_time()
        
        session_type = "Work Session" if self.timer.is_work_session else "Break Time"
        self.session_info_label.text = f"{session_type} • Session {self.timer.session_count + 1}"
        
        self.progress_bar.value = self.timer.get_progress() * 100


class StatsCard(StosOSCard):
    """Statistics display card"""
    
    def __init__(self, title: str, stats_data: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.stats_data = stats_data
        
        self.size_hint_y = None
        self.height = dp(150)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the statistics card UI"""
        layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # Title
        title_label = StosOSLabel(
            text=self.title,
            label_type="subtitle",
            halign='center',
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(title_label)
        
        # Stats grid
        stats_grid = GridLayout(cols=2, spacing=StosOSTheme.get_spacing('sm'))
        
        for key, value in self.stats_data.items():
            # Key label
            key_label = StosOSLabel(
                text=key.replace('_', ' ').title() + ":",
                color=StosOSTheme.get_color('text_secondary'),
                halign='left'
            )
            key_label.bind(size=key_label.setter('text_size'))
            stats_grid.add_widget(key_label)
            
            # Value label
            if isinstance(value, (int, float)):
                if 'minutes' in key.lower():
                    # Format minutes as hours and minutes
                    hours = int(value // 60)
                    mins = int(value % 60)
                    if hours > 0:
                        value_text = f"{hours}h {mins}m"
                    else:
                        value_text = f"{mins}m"
                else:
                    value_text = str(value)
            else:
                value_text = str(value)
            
            value_label = StosOSLabel(
                text=value_text,
                color=StosOSTheme.get_color('accent_secondary'),
                halign='right'
            )
            value_label.bind(size=value_label.setter('text_size'))
            stats_grid.add_widget(value_label)
        
        layout.add_widget(stats_grid)
        
        self.add_widget(layout)


class GoalCard(StosOSCard):
    """Study goal display and progress card"""
    
    def __init__(self, goal: StudyGoal, progress_minutes: int, **kwargs):
        super().__init__(**kwargs)
        self.goal = goal
        self.progress_minutes = progress_minutes
        
        self.size_hint_y = None
        self.height = dp(120)
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the goal card UI"""
        layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # Goal title
        title_label = StosOSLabel(
            text=f"📚 {self.goal.subject}",
            label_type="subtitle",
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(title_label)
        
        # Progress info
        progress_text = f"{self.progress_minutes} / {self.goal.daily_minutes} minutes today"
        progress_label = StosOSLabel(
            text=progress_text,
            color=StosOSTheme.get_color('text_secondary'),
            size_hint_y=None,
            height=dp(20)
        )
        layout.add_widget(progress_label)
        
        # Progress bar
        progress_percentage = min(100, (self.progress_minutes / self.goal.daily_minutes) * 100)
        progress_bar = StosOSProgressBar(
            value=progress_percentage,
            size_hint_y=None,
            height=dp(8)
        )
        layout.add_widget(progress_bar)
        
        # Achievement status
        if self.progress_minutes >= self.goal.daily_minutes:
            status_text = "🎉 Goal achieved!"
            status_color = StosOSTheme.get_color('success')
        elif self.progress_minutes >= self.goal.daily_minutes * 0.8:
            status_text = "🔥 Almost there!"
            status_color = StosOSTheme.get_color('warning')
        else:
            remaining = self.goal.daily_minutes - self.progress_minutes
            status_text = f"⏰ {remaining} minutes to go"
            status_color = StosOSTheme.get_color('text_secondary')
        
        status_label = StosOSLabel(
            text=status_text,
            color=status_color,
            size_hint_y=None,
            height=dp(25)
        )
        layout.add_widget(status_label)
        
        self.add_widget(layout)


class StudyTracker(BaseModule):
    """
    Study Tracker Module
    
    Provides comprehensive study tracking and productivity features including
    time tracking, Pomodoro timer, statistics, goals, and motivation.
    """
    
    def __init__(self):
        super().__init__(
            module_id="study_tracker",
            display_name="Study Tracker",
            icon="📊"
        )
        
        self.db_manager = None
        self.sessions = []
        self.goals = []
        self.current_session = None
        
        # UI components
        self.pomodoro_card = None
        self.stats_container = None
        self.goals_container = None
        
        # Update timer
        self.update_timer = None
    
    def initialize(self) -> bool:
        """Initialize the study tracker module"""
        try:
            self.db_manager = DatabaseManager()
            self._load_data()
            self._start_update_timer()
            self._initialized = True
            self.logger.info("Study Tracker module initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Study Tracker: {e}")
            self.handle_error(e, "initialization")
            return False
    
    def get_screen(self) -> Screen:
        """Get the study tracker screen"""
        if self.screen_widget is None:
            self.screen_widget = Screen(name=self.module_id)
            self._build_ui()
        return self.screen_widget
    
    def _build_ui(self):
        """Build the study tracker UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Header
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=StosOSTheme.get_spacing('md')
        )
        
        title_label = StosOSLabel(
            text="📊 Study Tracker",
            label_type="title",
            size_hint_x=0.6
        )
        header_layout.add_widget(title_label)
        
        # Streak counter
        streak_count = self._get_current_streak()
        streak_label = StosOSLabel(
            text=f"🔥 {streak_count} day streak",
            color=StosOSTheme.get_color('accent_secondary'),
            size_hint_x=0.4,
            halign='right'
        )
        streak_label.bind(size=streak_label.setter('text_size'))
        header_layout.add_widget(streak_label)
        
        main_layout.add_widget(header_layout)
        
        # Scrollable content
        scroll_view = StosOSScrollView()
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=StosOSTheme.get_spacing('md'),
            size_hint_y=None
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Pomodoro timer
        self.pomodoro_card = PomodoroCard(self)
        content_layout.add_widget(self.pomodoro_card)
        
        # Quick session controls
        self._build_session_controls(content_layout)
        
        # Statistics section
        self._build_statistics_section(content_layout)
        
        # Goals section
        self._build_goals_section(content_layout)
        
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        
        self.screen_widget.add_widget(main_layout)
    
    def _build_session_controls(self, parent_layout):
        """Build quick session start/stop controls"""
        session_panel = StosOSPanel(
            title="Quick Study Session",
            size_hint_y=None,
            height=dp(120)
        )
        
        controls_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # Subject input and start button
        input_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        self.subject_input = StosOSTextInput(
            placeholder="Subject (e.g., Physics, Math)",
            text="General",
            size_hint_x=0.7
        )
        input_layout.add_widget(self.subject_input)
        
        self.session_btn = StosOSButton(
            text="Start Session",
            button_type="accent",
            size_hint_x=0.3
        )
        self.session_btn.bind(on_press=self._toggle_study_session)
        input_layout.add_widget(self.session_btn)
        
        controls_layout.add_widget(input_layout)
        
        # Current session info
        self.session_info_label = StosOSLabel(
            text="No active session",
            color=StosOSTheme.get_color('text_secondary'),
            size_hint_y=None,
            height=dp(25)
        )
        controls_layout.add_widget(self.session_info_label)
        
        session_panel.add_widget(controls_layout)
        parent_layout.add_widget(session_panel)
    
    def _build_statistics_section(self, parent_layout):
        """Build statistics display section"""
        stats_panel = StosOSPanel(
            title="📈 Statistics",
            size_hint_y=None,
            height=dp(200)
        )
        
        self.stats_container = BoxLayout(
            orientation='horizontal',
            spacing=StosOSTheme.get_spacing('md')
        )
        
        # Will be populated by _update_statistics()
        self._update_statistics()
        
        stats_panel.add_widget(self.stats_container)
        parent_layout.add_widget(stats_panel)
    
    def _build_goals_section(self, parent_layout):
        """Build goals display section"""
        goals_panel = StosOSPanel(
            title="🎯 Study Goals",
            size_hint_y=None,
            height=dp(180)
        )
        
        goals_layout = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('sm'))
        
        # Add goal button
        add_goal_btn = StosOSButton(
            text="+ Add Goal",
            button_type="secondary",
            size_hint_y=None,
            height=dp(35)
        )
        add_goal_btn.bind(on_press=self._show_add_goal_form)
        goals_layout.add_widget(add_goal_btn)
        
        # Goals container
        self.goals_container = BoxLayout(
            orientation='horizontal',
            spacing=StosOSTheme.get_spacing('md')
        )
        
        # Will be populated by _update_goals()
        self._update_goals()
        
        goals_layout.add_widget(self.goals_container)
        goals_panel.add_widget(goals_layout)
        parent_layout.add_widget(goals_panel)
    
    def _load_data(self):
        """Load study sessions and goals from database"""
        try:
            # Load study sessions
            self.sessions = self.db_manager.get_study_sessions()
            
            # Load goals (stored as JSON in settings or separate table)
            # For now, create some default goals
            self.goals = [
                StudyGoal("Physics", 120),  # 2 hours daily
                StudyGoal("Mathematics", 90),  # 1.5 hours daily
                StudyGoal("Chemistry", 60)   # 1 hour daily
            ]
            
            self.logger.debug(f"Loaded {len(self.sessions)} study sessions and {len(self.goals)} goals")
        except Exception as e:
            self.logger.error(f"Failed to load study data: {e}")
            self.sessions = []
            self.goals = []
    
    def _start_update_timer(self):
        """Start timer for regular UI updates"""
        self.update_timer = Clock.schedule_interval(self._update_ui, 30.0)  # Update every 30 seconds
    
    def _update_ui(self, dt=None):
        """Update UI components with current data"""
        if hasattr(self, 'session_info_label'):
            self._update_session_info()
        if hasattr(self, 'stats_container'):
            self._update_statistics()
        if hasattr(self, 'goals_container'):
            self._update_goals()
    
    def _toggle_study_session(self, *args):
        """Start or stop a study session"""
        if self.current_session is None:
            # Start new session
            subject = self.subject_input.text.strip() or "General"
            self.current_session = StudySession(subject=subject)
            self.session_btn.text = "End Session"
            self.session_btn.button_type = "danger"
            self.logger.info(f"Started study session for {subject}")
        else:
            # End current session
            self.current_session.end_session()
            
            # Save to database
            try:
                if self.db_manager.create_study_session(self.current_session):
                    self.sessions.append(self.current_session)
                    self.logger.info(f"Ended study session: {self.current_session.get_formatted_duration()}")
                else:
                    self.logger.error("Failed to save study session")
            except Exception as e:
                self.logger.error(f"Error saving study session: {e}")
            
            self.current_session = None
            self.session_btn.text = "Start Session"
            self.session_btn.button_type = "accent"
        
        self._update_session_info()
    
    def _update_session_info(self):
        """Update current session information"""
        if self.current_session:
            duration = self.current_session.get_formatted_duration()
            self.session_info_label.text = f"📚 Studying {self.current_session.subject} • {duration}"
            self.session_info_label.color = StosOSTheme.get_color('accent_secondary')
        else:
            self.session_info_label.text = "No active session"
            self.session_info_label.color = StosOSTheme.get_color('text_secondary')
    
    def _update_statistics(self):
        """Update statistics display"""
        if not hasattr(self, 'stats_container'):
            return
        
        self.stats_container.clear_widgets()
        
        stats = StudyStats(self.sessions)
        
        # Today's stats
        today_stats = stats.get_daily_stats()
        today_card = StatsCard("Today", {
            'Total Time': today_stats['total_minutes'],
            'Sessions': today_stats['session_count'],
            'Subjects': len(today_stats['subject_breakdown'])
        })
        self.stats_container.add_widget(today_card)
        
        # This week's stats
        week_stats = stats.get_weekly_stats()
        week_card = StatsCard("This Week", {
            'Total Time': week_stats['total_minutes'],
            'Daily Average': int(week_stats['average_daily_minutes']),
            'Sessions': week_stats['session_count']
        })
        self.stats_container.add_widget(week_card)
    
    def _update_goals(self):
        """Update goals display"""
        if not hasattr(self, 'goals_container'):
            return
        
        self.goals_container.clear_widgets()
        
        # Get today's progress for each goal
        stats = StudyStats(self.sessions)
        today_stats = stats.get_daily_stats()
        
        for goal in self.goals:
            progress_minutes = today_stats['subject_breakdown'].get(goal.subject, 0)
            goal_card = GoalCard(goal, progress_minutes)
            self.goals_container.add_widget(goal_card)
        
        # Show message if no goals
        if not self.goals:
            no_goals_label = StosOSLabel(
                text="No study goals set. Add a goal to track your progress!",
                halign='center',
                color=StosOSTheme.get_color('text_disabled')
            )
            no_goals_label.bind(size=no_goals_label.setter('text_size'))
            self.goals_container.add_widget(no_goals_label)
    
    def _get_current_streak(self) -> int:
        """Get current study streak"""
        stats = StudyStats(self.sessions)
        return stats.get_streak_count()
    
    def _show_add_goal_form(self, *args):
        """Show form for adding new study goal"""
        content = BoxLayout(orientation='vertical', spacing=StosOSTheme.get_spacing('md'))
        
        # Subject input
        subject_input = StosOSTextInput(
            placeholder="Subject name",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        content.add_widget(StosOSLabel(text="Subject:", size_hint_y=None, height=dp(25)))
        content.add_widget(subject_input)
        
        # Daily minutes input
        minutes_input = StosOSTextInput(
            placeholder="Daily minutes target",
            text="60",
            size_hint_y=None,
            height=StosOSTheme.get_dimension('input_height')
        )
        content.add_widget(StosOSLabel(text="Daily Target (minutes):", size_hint_y=None, height=dp(25)))
        content.add_widget(minutes_input)
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', spacing=StosOSTheme.get_spacing('md'))
        
        cancel_btn = StosOSButton(text="Cancel", button_type="secondary")
        save_btn = StosOSButton(text="Save Goal", button_type="accent")
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(save_btn)
        content.add_widget(button_layout)
        
        popup = StosOSPopup(
            title="Add Study Goal",
            content=content,
            size_hint=(0.6, 0.5)
        )
        
        def save_goal(*args):
            try:
                subject = subject_input.text.strip()
                daily_minutes = int(minutes_input.text.strip())
                
                if subject and daily_minutes > 0:
                    goal = StudyGoal(subject, daily_minutes)
                    self.goals.append(goal)
                    self._update_goals()
                    popup.dismiss()
                    self.logger.info(f"Added study goal: {subject} - {daily_minutes} minutes/day")
            except ValueError:
                # Invalid input - could show error
                pass
        
        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=save_goal)
        
        popup.open_with_animation()
    
    def handle_voice_command(self, command: str) -> bool:
        """Handle voice commands for study tracker"""
        command_lower = command.lower()
        
        if "start study" in command_lower or "begin study" in command_lower:
            if self.current_session is None:
                # Extract subject if mentioned
                subject = "General"
                for goal in self.goals:
                    if goal.subject.lower() in command_lower:
                        subject = goal.subject
                        break
                
                self.subject_input.text = subject
                self._toggle_study_session()
                return True
        
        elif "end study" in command_lower or "stop study" in command_lower:
            if self.current_session is not None:
                self._toggle_study_session()
                return True
        
        elif "start pomodoro" in command_lower:
            if hasattr(self, 'pomodoro_card'):
                self.pomodoro_card._toggle_timer()
                return True
        
        elif "study stats" in command_lower or "study statistics" in command_lower:
            # Could announce current statistics
            return True
        
        return False
    
    def on_activate(self):
        """Called when module becomes active"""
        super().on_activate()
        self._update_ui()
    
    def cleanup(self):
        """Cleanup module resources"""
        if self.update_timer:
            self.update_timer.cancel()
            self.update_timer = None
        
        if self.current_session:
            # Auto-save current session
            self.current_session.end_session()
            try:
                self.db_manager.create_study_session(self.current_session)
                self.sessions.append(self.current_session)
            except Exception as e:
                self.logger.error(f"Error auto-saving session on cleanup: {e}")
        
        super().cleanup()