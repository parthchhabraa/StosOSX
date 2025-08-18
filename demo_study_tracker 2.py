#!/usr/bin/env python3
"""
Demo script for StudyTracker module.

This script demonstrates the study tracking functionality including:
- Pomodoro timer
- Study session management
- Statistics calculation
- Goal tracking
- Streak counting
"""

import sys
import os
from datetime import datetime, timedelta, date
from pathlib import Path

# Add the parent directory to the path so we can import stosos modules
sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock

from core.database_manager import DatabaseManager
from models.study_session import StudySession
from modules.study_tracker import StudyTracker, StudyStats, StudyGoal, PomodoroTimer


class StudyTrackerDemoApp(App):
    """Demo app for StudyTracker module"""
    
    def build(self):
        """Build the demo app"""
        self.title = "StosOS Study Tracker Demo"
        
        # Initialize database and create sample data
        self.setup_sample_data()
        
        # Create and initialize the study tracker module
        self.study_tracker = StudyTracker()
        if not self.study_tracker.initialize():
            print("Failed to initialize StudyTracker module")
            return BoxLayout()
        
        # Get the study tracker screen
        screen = self.study_tracker.get_screen()
        
        # Activate the module
        self.study_tracker.on_activate()
        
        return screen
    
    def setup_sample_data(self):
        """Create sample study sessions for demonstration"""
        db_manager = DatabaseManager()
        
        # Create sample study sessions over the past week
        sample_sessions = []
        
        # Today's sessions
        today = datetime.now()
        sample_sessions.extend([
            StudySession(
                subject="Physics",
                start_time=today.replace(hour=9, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=10, minute=30, second=0, microsecond=0),
                notes="Studied mechanics - Newton's laws"
            ),
            StudySession(
                subject="Mathematics",
                start_time=today.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=15, minute=45, second=0, microsecond=0),
                notes="Calculus practice problems"
            )
        ])
        
        # Yesterday's sessions
        yesterday = today - timedelta(days=1)
        sample_sessions.extend([
            StudySession(
                subject="Chemistry",
                start_time=yesterday.replace(hour=10, minute=0, second=0, microsecond=0),
                end_time=yesterday.replace(hour=11, minute=30, second=0, microsecond=0),
                notes="Organic chemistry reactions"
            ),
            StudySession(
                subject="Physics",
                start_time=yesterday.replace(hour=15, minute=0, second=0, microsecond=0),
                end_time=yesterday.replace(hour=16, minute=20, second=0, microsecond=0),
                notes="Thermodynamics concepts"
            )
        ])
        
        # Sessions from 2 days ago
        two_days_ago = today - timedelta(days=2)
        sample_sessions.extend([
            StudySession(
                subject="Mathematics",
                start_time=two_days_ago.replace(hour=9, minute=30, second=0, microsecond=0),
                end_time=two_days_ago.replace(hour=11, minute=0, second=0, microsecond=0),
                notes="Linear algebra matrices"
            ),
            StudySession(
                subject="Physics",
                start_time=two_days_ago.replace(hour=16, minute=0, second=0, microsecond=0),
                end_time=two_days_ago.replace(hour=17, minute=15, second=0, microsecond=0),
                notes="Electromagnetic fields"
            )
        ])
        
        # Sessions from 3 days ago
        three_days_ago = today - timedelta(days=3)
        sample_sessions.extend([
            StudySession(
                subject="Chemistry",
                start_time=three_days_ago.replace(hour=11, minute=0, second=0, microsecond=0),
                end_time=three_days_ago.replace(hour=12, minute=45, second=0, microsecond=0),
                notes="Chemical bonding theory"
            )
        ])
        
        # Save sample sessions to database
        for session in sample_sessions:
            try:
                db_manager.create_study_session(session)
                print(f"Created sample session: {session.subject} - {session.get_formatted_duration()}")
            except Exception as e:
                print(f"Error creating sample session: {e}")
        
        print(f"Created {len(sample_sessions)} sample study sessions")
    
    def on_stop(self):
        """Cleanup when app stops"""
        if hasattr(self, 'study_tracker'):
            self.study_tracker.cleanup()


def test_pomodoro_timer():
    """Test the Pomodoro timer functionality"""
    print("\n=== Testing Pomodoro Timer ===")
    
    def on_tick(remaining_time, is_work_session):
        session_type = "Work" if is_work_session else "Break"
        minutes = remaining_time // 60
        seconds = remaining_time % 60
        print(f"{session_type}: {minutes:02d}:{seconds:02d}")
    
    def on_complete(next_is_work, session_count):
        session_type = "Work" if next_is_work else "Break"
        print(f"Session completed! Next: {session_type}, Total sessions: {session_count}")
    
    timer = PomodoroTimer(on_tick=on_tick, on_complete=on_complete)
    
    # Test timer properties
    print(f"Initial time: {timer.get_formatted_time()}")
    print(f"Is work session: {timer.is_work_session}")
    print(f"Progress: {timer.get_progress():.2%}")
    
    # Simulate some time passing
    timer.current_time = 5  # 5 seconds left
    print(f"Time remaining: {timer.get_formatted_time()}")
    
    # Test completion
    timer._complete_session()
    print(f"After completion - Is work session: {timer.is_work_session}")
    print(f"New time: {timer.get_formatted_time()}")


def test_study_stats():
    """Test the StudyStats functionality"""
    print("\n=== Testing Study Statistics ===")
    
    # Create sample sessions
    sessions = []
    today = datetime.now()
    
    # Today's sessions
    sessions.append(StudySession(
        subject="Physics",
        start_time=today.replace(hour=9, minute=0),
        end_time=today.replace(hour=10, minute=30)
    ))
    sessions.append(StudySession(
        subject="Math",
        start_time=today.replace(hour=14, minute=0),
        end_time=today.replace(hour=15, minute=45)
    ))
    
    # Yesterday's sessions
    yesterday = today - timedelta(days=1)
    sessions.append(StudySession(
        subject="Chemistry",
        start_time=yesterday.replace(hour=10, minute=0),
        end_time=yesterday.replace(hour=11, minute=30)
    ))
    
    stats = StudyStats(sessions)
    
    # Test daily stats
    daily_stats = stats.get_daily_stats()
    print(f"Today's stats:")
    print(f"  Total time: {daily_stats['total_minutes']} minutes")
    print(f"  Sessions: {daily_stats['session_count']}")
    print(f"  Subjects: {list(daily_stats['subject_breakdown'].keys())}")
    
    # Test weekly stats
    weekly_stats = stats.get_weekly_stats()
    print(f"\nWeekly stats:")
    print(f"  Total time: {weekly_stats['total_minutes']} minutes")
    print(f"  Average daily: {weekly_stats['average_daily_minutes']:.1f} minutes")
    print(f"  Sessions: {weekly_stats['session_count']}")
    
    # Test streak
    streak = stats.get_streak_count()
    print(f"\nCurrent streak: {streak} days")
    
    # Test subject progress
    physics_progress = stats.get_subject_progress("Physics", days=7)
    print(f"\nPhysics progress (7 days):")
    print(f"  Total time: {physics_progress['total_minutes']} minutes")
    print(f"  Sessions: {physics_progress['session_count']}")
    print(f"  Average daily: {physics_progress['average_daily_minutes']:.1f} minutes")


def test_study_goals():
    """Test the StudyGoal functionality"""
    print("\n=== Testing Study Goals ===")
    
    # Create sample goals
    goals = [
        StudyGoal("Physics", 120),  # 2 hours daily
        StudyGoal("Mathematics", 90),  # 1.5 hours daily
        StudyGoal("Chemistry", 60)   # 1 hour daily
    ]
    
    for goal in goals:
        print(f"Goal: {goal.subject}")
        print(f"  Daily target: {goal.daily_minutes} minutes")
        print(f"  Weekly target: {goal.weekly_minutes} minutes")
        print(f"  Created: {goal.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        # Test serialization
        goal_dict = goal.to_dict()
        restored_goal = StudyGoal.from_dict(goal_dict)
        print(f"  Serialization test: {restored_goal.subject == goal.subject}")


def main():
    """Main function to run tests or demo app"""
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run unit tests
        test_pomodoro_timer()
        test_study_stats()
        test_study_goals()
    else:
        # Run the demo app
        print("Starting StudyTracker Demo App...")
        print("Use 'python demo_study_tracker.py test' to run unit tests")
        
        try:
            app = StudyTrackerDemoApp()
            app.run()
        except Exception as e:
            print(f"Error running demo app: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()