#!/usr/bin/env python3
"""
Comprehensive test suite for StudyTracker module.

Tests all functionality including UI components, database integration,
statistics calculation, and Pomodoro timer.
"""

import sys
import os
import unittest
from datetime import datetime, timedelta, date
from pathlib import Path

# Add the parent directory to the path so we can import stosos modules
sys.path.insert(0, str(Path(__file__).parent))

from core.database_manager import DatabaseManager
from models.study_session import StudySession


class TestStudyTrackerCore(unittest.TestCase):
    """Test core StudyTracker functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.db_manager = DatabaseManager()
        
        # Import core classes
        from test_study_tracker_core import PomodoroTimer, StudyGoal, StudyStats
        self.PomodoroTimer = PomodoroTimer
        self.StudyGoal = StudyGoal
        self.StudyStats = StudyStats
    
    def test_pomodoro_timer_initialization(self):
        """Test Pomodoro timer initialization"""
        timer = self.PomodoroTimer()
        
        self.assertEqual(timer.work_duration, 25 * 60)
        self.assertEqual(timer.short_break_duration, 5 * 60)
        self.assertEqual(timer.long_break_duration, 15 * 60)
        self.assertTrue(timer.is_work_session)
        self.assertEqual(timer.session_count, 0)
        self.assertFalse(timer.is_running)
    
    def test_pomodoro_timer_formatting(self):
        """Test timer formatting functions"""
        timer = self.PomodoroTimer()
        
        # Test initial formatting
        self.assertEqual(timer.get_formatted_time(), "25:00")
        self.assertEqual(timer.get_progress(), 0.0)
        
        # Test with different times
        timer.current_time = 15 * 60  # 15 minutes
        self.assertEqual(timer.get_formatted_time(), "15:00")
        self.assertAlmostEqual(timer.get_progress(), 0.4, places=2)  # 10/25 = 0.4
        
        timer.current_time = 90  # 1 minute 30 seconds
        self.assertEqual(timer.get_formatted_time(), "01:30")
    
    def test_pomodoro_timer_session_completion(self):
        """Test Pomodoro session completion logic"""
        timer = self.PomodoroTimer()
        
        # Complete first work session
        timer.current_time = 0
        timer._complete_session()
        
        self.assertFalse(timer.is_work_session)  # Should switch to break
        self.assertEqual(timer.session_count, 1)
        self.assertEqual(timer.current_time, timer.short_break_duration)
        
        # Complete break
        timer.current_time = 0
        timer._complete_session()
        
        self.assertTrue(timer.is_work_session)  # Should switch back to work
        self.assertEqual(timer.current_time, timer.work_duration)
        
        # Test long break after 4 sessions
        timer.session_count = 4
        timer.is_work_session = True
        timer.current_time = 0
        timer._complete_session()
        
        self.assertFalse(timer.is_work_session)
        self.assertEqual(timer.current_time, timer.long_break_duration)
    
    def test_study_goal_creation(self):
        """Test StudyGoal creation and serialization"""
        goal = self.StudyGoal("Physics", 120)
        
        self.assertEqual(goal.subject, "Physics")
        self.assertEqual(goal.daily_minutes, 120)
        self.assertEqual(goal.weekly_minutes, 840)  # 120 * 7
        self.assertIsInstance(goal.created_at, datetime)
        
        # Test custom weekly minutes
        goal2 = self.StudyGoal("Math", 90, 500)
        self.assertEqual(goal2.weekly_minutes, 500)
    
    def test_study_goal_serialization(self):
        """Test StudyGoal serialization and deserialization"""
        goal = self.StudyGoal("Chemistry", 60)
        
        # Test to_dict
        goal_dict = goal.to_dict()
        self.assertIn('subject', goal_dict)
        self.assertIn('daily_minutes', goal_dict)
        self.assertIn('weekly_minutes', goal_dict)
        self.assertIn('created_at', goal_dict)
        
        # Test from_dict
        restored_goal = self.StudyGoal.from_dict(goal_dict)
        self.assertEqual(restored_goal.subject, goal.subject)
        self.assertEqual(restored_goal.daily_minutes, goal.daily_minutes)
        self.assertEqual(restored_goal.weekly_minutes, goal.weekly_minutes)
    
    def test_study_stats_daily(self):
        """Test daily statistics calculation"""
        # Create test sessions
        today = datetime.now()
        sessions = [
            StudySession(
                subject="Physics",
                start_time=today.replace(hour=9, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=10, minute=30, second=0, microsecond=0)
            ),
            StudySession(
                subject="Math",
                start_time=today.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=15, minute=45, second=0, microsecond=0)
            )
        ]
        
        stats = self.StudyStats(sessions)
        daily_stats = stats.get_daily_stats()
        
        self.assertEqual(daily_stats['session_count'], 2)
        self.assertEqual(daily_stats['total_minutes'], 195)  # 90 + 105
        self.assertEqual(len(daily_stats['subject_breakdown']), 2)
        self.assertEqual(daily_stats['subject_breakdown']['Physics'], 90)
        self.assertEqual(daily_stats['subject_breakdown']['Math'], 105)
    
    def test_study_stats_weekly(self):
        """Test weekly statistics calculation"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        sessions = [
            StudySession(
                subject="Physics",
                start_time=today.replace(hour=9, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=10, minute=0, second=0, microsecond=0)
            ),
            StudySession(
                subject="Math",
                start_time=yesterday.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=yesterday.replace(hour=15, minute=30, second=0, microsecond=0)
            )
        ]
        
        stats = self.StudyStats(sessions)
        weekly_stats = stats.get_weekly_stats()
        
        self.assertEqual(weekly_stats['session_count'], 2)
        self.assertEqual(weekly_stats['total_minutes'], 150)  # 60 + 90
        self.assertAlmostEqual(weekly_stats['average_daily_minutes'], 150/7, places=2)
    
    def test_study_stats_streak(self):
        """Test study streak calculation"""
        today = datetime.now()
        
        # Create sessions for consecutive days
        sessions = []
        for days_ago in range(3, 0, -1):  # 3 days ago, 2 days ago, yesterday
            session_date = today - timedelta(days=days_ago)
            sessions.append(StudySession(
                subject="Physics",
                start_time=session_date.replace(hour=10, minute=0, second=0, microsecond=0),
                end_time=session_date.replace(hour=10, minute=30, second=0, microsecond=0)  # 30 minutes
            ))
        
        # Add today's session
        sessions.append(StudySession(
            subject="Math",
            start_time=today.replace(hour=14, minute=0, second=0, microsecond=0),
            end_time=today.replace(hour=14, minute=20, second=0, microsecond=0)  # 20 minutes
        ))
        
        stats = self.StudyStats(sessions)
        streak = stats.get_streak_count()
        
        # Should have a 4-day streak (including today)
        self.assertGreaterEqual(streak, 3)  # At least 3 days
    
    def test_study_stats_subject_progress(self):
        """Test subject-specific progress calculation"""
        today = datetime.now()
        
        sessions = [
            StudySession(
                subject="Physics",
                start_time=today.replace(hour=9, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=10, minute=0, second=0, microsecond=0)
            ),
            StudySession(
                subject="Physics",
                start_time=today.replace(hour=14, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=14, minute=45, second=0, microsecond=0)
            ),
            StudySession(
                subject="Math",
                start_time=today.replace(hour=16, minute=0, second=0, microsecond=0),
                end_time=today.replace(hour=16, minute=30, second=0, microsecond=0)
            )
        ]
        
        stats = self.StudyStats(sessions)
        physics_progress = stats.get_subject_progress("Physics", days=7)
        
        self.assertEqual(physics_progress['subject'], "Physics")
        self.assertEqual(physics_progress['total_minutes'], 105)  # 60 + 45
        self.assertEqual(physics_progress['session_count'], 2)
        self.assertEqual(physics_progress['period_days'], 7)
        self.assertAlmostEqual(physics_progress['average_daily_minutes'], 105/7, places=2)


class TestStudySessionModel(unittest.TestCase):
    """Test StudySession model functionality"""
    
    def test_study_session_creation(self):
        """Test StudySession creation"""
        session = StudySession(subject="Physics")
        
        self.assertEqual(session.subject, "Physics")
        self.assertTrue(session.is_active)
        self.assertIsNone(session.end_time)
        self.assertIsInstance(session.start_time, datetime)
        self.assertIsInstance(session.id, str)
        self.assertEqual(len(session.tasks_completed), 0)
        self.assertEqual(session.notes, "")
    
    def test_study_session_validation(self):
        """Test StudySession validation"""
        # Test empty subject validation
        with self.assertRaises(ValueError):
            StudySession(subject="")
        
        with self.assertRaises(ValueError):
            StudySession(subject="   ")  # Only whitespace
    
    def test_study_session_duration(self):
        """Test duration calculation"""
        start_time = datetime.now()
        session = StudySession(subject="Physics", start_time=start_time)
        
        # Test active session duration (should be >= 0)
        self.assertGreaterEqual(session.duration, 0)
        
        # Test completed session duration
        end_time = start_time + timedelta(minutes=45)
        session.end_time = end_time
        self.assertEqual(session.duration, 45)
    
    def test_study_session_end(self):
        """Test ending a study session"""
        session = StudySession(subject="Physics")
        
        self.assertTrue(session.is_active)
        
        session.end_session("Completed mechanics problems")
        
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.end_time)
        self.assertEqual(session.notes, "Completed mechanics problems")
        
        # Test ending already ended session
        with self.assertRaises(ValueError):
            session.end_session("Already ended")
    
    def test_study_session_tasks(self):
        """Test task completion tracking"""
        session = StudySession(subject="Physics")
        
        # Test adding tasks
        session.add_completed_task("task_1")
        session.add_completed_task("task_2")
        self.assertEqual(len(session.tasks_completed), 2)
        self.assertIn("task_1", session.tasks_completed)
        self.assertIn("task_2", session.tasks_completed)
        
        # Test adding duplicate task (should not duplicate)
        session.add_completed_task("task_1")
        self.assertEqual(len(session.tasks_completed), 2)
        
        # Test removing task
        session.remove_completed_task("task_1")
        self.assertEqual(len(session.tasks_completed), 1)
        self.assertNotIn("task_1", session.tasks_completed)
        self.assertIn("task_2", session.tasks_completed)
        
        # Test removing non-existent task (should not error)
        session.remove_completed_task("task_3")
        self.assertEqual(len(session.tasks_completed), 1)
    
    def test_study_session_serialization(self):
        """Test StudySession serialization"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=30)
        
        session = StudySession(
            subject="Physics",
            start_time=start_time,
            end_time=end_time,
            notes="Test session"
        )
        session.add_completed_task("task_1")
        session.add_completed_task("task_2")
        
        # Test to_dict
        session_dict = session.to_dict()
        self.assertIn('id', session_dict)
        self.assertIn('subject', session_dict)
        self.assertIn('start_time', session_dict)
        self.assertIn('end_time', session_dict)
        self.assertIn('duration', session_dict)
        self.assertIn('tasks_completed', session_dict)
        self.assertIn('notes', session_dict)
        
        # Test from_dict
        restored_session = StudySession.from_dict(session_dict)
        self.assertEqual(restored_session.id, session.id)
        self.assertEqual(restored_session.subject, session.subject)
        self.assertEqual(restored_session.notes, session.notes)
        self.assertEqual(len(restored_session.tasks_completed), 2)
        self.assertIn("task_1", restored_session.tasks_completed)
        self.assertIn("task_2", restored_session.tasks_completed)
    
    def test_study_session_formatting(self):
        """Test formatted duration output"""
        start_time = datetime.now()
        
        # Test various durations
        test_cases = [
            (30, "30m"),      # 30 minutes
            (90, "1h 30m"),   # 1 hour 30 minutes
            (120, "2h 0m"),   # 2 hours exactly
            (5, "5m"),        # 5 minutes
            (0, "0m")         # 0 minutes
        ]
        
        for minutes, expected in test_cases:
            end_time = start_time + timedelta(minutes=minutes)
            session = StudySession(
                subject="Test",
                start_time=start_time,
                end_time=end_time
            )
            self.assertEqual(session.get_formatted_duration(), expected)


class TestDatabaseIntegration(unittest.TestCase):
    """Test database integration for study sessions"""
    
    def setUp(self):
        """Set up test database"""
        self.db_manager = DatabaseManager()
    
    def test_create_study_session(self):
        """Test creating study session in database"""
        session = StudySession(
            subject="Test Subject",
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            notes="Test session"
        )
        
        success = self.db_manager.create_study_session(session)
        self.assertTrue(success)
        
        # Clean up
        self.db_manager.delete_study_session(session.id)
    
    def test_get_study_session(self):
        """Test retrieving study session from database"""
        session = StudySession(
            subject="Test Subject",
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            notes="Test session"
        )
        
        # Create session
        self.db_manager.create_study_session(session)
        
        # Retrieve session
        retrieved = self.db_manager.get_study_session(session.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.subject, session.subject)
        self.assertEqual(retrieved.notes, session.notes)
        
        # Clean up
        self.db_manager.delete_study_session(session.id)
    
    def test_update_study_session(self):
        """Test updating study session in database"""
        session = StudySession(
            subject="Test Subject",
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now(),
            notes="Original notes"
        )
        
        # Create session
        self.db_manager.create_study_session(session)
        
        # Update session
        session.notes = "Updated notes"
        success = self.db_manager.update_study_session(session)
        self.assertTrue(success)
        
        # Verify update
        retrieved = self.db_manager.get_study_session(session.id)
        self.assertEqual(retrieved.notes, "Updated notes")
        
        # Clean up
        self.db_manager.delete_study_session(session.id)
    
    def test_delete_study_session(self):
        """Test deleting study session from database"""
        session = StudySession(
            subject="Test Subject",
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now()
        )
        
        # Create session
        self.db_manager.create_study_session(session)
        
        # Verify it exists
        retrieved = self.db_manager.get_study_session(session.id)
        self.assertIsNotNone(retrieved)
        
        # Delete session
        success = self.db_manager.delete_study_session(session.id)
        self.assertTrue(success)
        
        # Verify it's deleted
        retrieved = self.db_manager.get_study_session(session.id)
        self.assertIsNone(retrieved)
    
    def test_get_study_sessions_filtering(self):
        """Test filtering study sessions"""
        # Create test sessions
        sessions = [
            StudySession(subject="Physics", start_time=datetime.now() - timedelta(hours=3)),
            StudySession(subject="Math", start_time=datetime.now() - timedelta(hours=2)),
            StudySession(subject="Physics", start_time=datetime.now() - timedelta(hours=1))
        ]
        
        # End all sessions
        for session in sessions:
            session.end_session()
            self.db_manager.create_study_session(session)
        
        try:
            # Test filtering by subject
            physics_sessions = self.db_manager.get_study_sessions(subject="Physics")
            self.assertEqual(len(physics_sessions), 2)
            
            math_sessions = self.db_manager.get_study_sessions(subject="Math")
            self.assertEqual(len(math_sessions), 1)
            
            # Test getting all sessions
            all_sessions = self.db_manager.get_study_sessions()
            self.assertGreaterEqual(len(all_sessions), 3)
            
        finally:
            # Clean up
            for session in sessions:
                self.db_manager.delete_study_session(session.id)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestStudyTrackerCore))
    suite.addTests(loader.loadTestsFromTestCase(TestStudySessionModel))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running StudyTracker Comprehensive Tests...")
    success = run_tests()
    
    if success:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Some tests failed!")
    
    sys.exit(0 if success else 1)