#!/usr/bin/env python3
"""
Simple test script for StudyTracker module functionality.

Tests core functionality without requiring full Kivy UI.
"""

import sys
import os
from datetime import datetime, timedelta, date
from pathlib import Path

# Add the parent directory to the path so we can import stosos modules
sys.path.insert(0, str(Path(__file__).parent))

from core.database_manager import DatabaseManager
from models.study_session import StudySession
from modules.study_tracker import StudyStats, StudyGoal, PomodoroTimer


def test_pomodoro_timer():
    """Test Pomodoro timer functionality"""
    print("Testing Pomodoro Timer...")
    
    # Test timer creation
    timer = PomodoroTimer()
    assert timer.work_duration == 25 * 60, "Work duration should be 25 minutes"
    assert timer.short_break_duration == 5 * 60, "Short break should be 5 minutes"
    assert timer.long_break_duration == 15 * 60, "Long break should be 15 minutes"
    assert timer.is_work_session == True, "Should start with work session"
    assert timer.current_time == timer.work_duration, "Should start with full work time"
    
    # Test formatted time
    formatted_time = timer.get_formatted_time()
    assert formatted_time == "25:00", f"Expected '25:00', got '{formatted_time}'"
    
    # Test progress calculation
    progress = timer.get_progress()
    assert progress == 0.0, f"Initial progress should be 0.0, got {progress}"
    
    # Simulate some time passing
    timer.current_time = 15 * 60  # 15 minutes left
    progress = timer.get_progress()
    expected_progress = 10/25  # 10 minutes elapsed out of 25
    assert abs(progress - expected_progress) < 0.01, f"Expected {expected_progress}, got {progress}"
    
    # Test session completion
    timer.current_time = 0
    timer._complete_session()
    assert timer.is_work_session == False, "Should switch to break after work session"
    assert timer.session_count == 1, "Session count should increment"
    
    print("✓ Pomodoro Timer tests passed")


def test_study_stats():
    """Test StudyStats functionality"""
    print("Testing Study Statistics...")
    
    # Create sample sessions
    sessions = []
    today = datetime.now()
    
    # Today's sessions
    sessions.append(StudySession(
        subject="Physics",
        start_time=today.replace(hour=9, minute=0, second=0, microsecond=0),
        end_time=today.replace(hour=10, minute=30, second=0, microsecond=0)
    ))
    sessions.append(StudySession(
        subject="Math",
        start_time=today.replace(hour=14, minute=0, second=0, microsecond=0),
        end_time=today.replace(hour=15, minute=45, second=0, microsecond=0)
    ))
    
    # Yesterday's sessions
    yesterday = today - timedelta(days=1)
    sessions.append(StudySession(
        subject="Chemistry",
        start_time=yesterday.replace(hour=10, minute=0, second=0, microsecond=0),
        end_time=yesterday.replace(hour=11, minute=30, second=0, microsecond=0)
    ))
    
    stats = StudyStats(sessions)
    
    # Test daily stats
    daily_stats = stats.get_daily_stats()
    assert daily_stats['session_count'] == 2, f"Expected 2 sessions today, got {daily_stats['session_count']}"
    assert daily_stats['total_minutes'] == 195, f"Expected 195 minutes today, got {daily_stats['total_minutes']}"  # 90 + 105
    assert len(daily_stats['subject_breakdown']) == 2, "Should have 2 subjects today"
    
    # Test weekly stats
    weekly_stats = stats.get_weekly_stats()
    assert weekly_stats['session_count'] == 3, f"Expected 3 sessions this week, got {weekly_stats['session_count']}"
    assert weekly_stats['total_minutes'] == 285, f"Expected 285 minutes this week, got {weekly_stats['total_minutes']}"  # 195 + 90
    
    # Test streak calculation
    streak = stats.get_streak_count()
    assert streak >= 1, f"Should have at least 1 day streak, got {streak}"
    
    # Test subject progress
    physics_progress = stats.get_subject_progress("Physics", days=7)
    assert physics_progress['total_minutes'] == 90, f"Expected 90 minutes for Physics, got {physics_progress['total_minutes']}"
    assert physics_progress['session_count'] == 1, f"Expected 1 Physics session, got {physics_progress['session_count']}"
    
    print("✓ Study Statistics tests passed")


def test_study_goals():
    """Test StudyGoal functionality"""
    print("Testing Study Goals...")
    
    # Test goal creation
    goal = StudyGoal("Physics", 120)
    assert goal.subject == "Physics", "Subject should be set correctly"
    assert goal.daily_minutes == 120, "Daily minutes should be set correctly"
    assert goal.weekly_minutes == 840, "Weekly minutes should be 7 * daily"  # 120 * 7
    
    # Test custom weekly minutes
    goal2 = StudyGoal("Math", 90, 500)
    assert goal2.weekly_minutes == 500, "Custom weekly minutes should be respected"
    
    # Test serialization
    goal_dict = goal.to_dict()
    assert 'subject' in goal_dict, "Dictionary should contain subject"
    assert 'daily_minutes' in goal_dict, "Dictionary should contain daily_minutes"
    assert 'weekly_minutes' in goal_dict, "Dictionary should contain weekly_minutes"
    assert 'created_at' in goal_dict, "Dictionary should contain created_at"
    
    # Test deserialization
    restored_goal = StudyGoal.from_dict(goal_dict)
    assert restored_goal.subject == goal.subject, "Subject should be restored correctly"
    assert restored_goal.daily_minutes == goal.daily_minutes, "Daily minutes should be restored correctly"
    assert restored_goal.weekly_minutes == goal.weekly_minutes, "Weekly minutes should be restored correctly"
    
    print("✓ Study Goals tests passed")


def test_database_integration():
    """Test database integration for study sessions"""
    print("Testing Database Integration...")
    
    db_manager = DatabaseManager()
    
    # Create a test study session
    session = StudySession(
        subject="Test Subject",
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now(),
        notes="Test session for integration"
    )
    
    # Test creation
    success = db_manager.create_study_session(session)
    assert success, "Should be able to create study session in database"
    
    # Test retrieval
    retrieved_session = db_manager.get_study_session(session.id)
    assert retrieved_session is not None, "Should be able to retrieve study session"
    assert retrieved_session.subject == session.subject, "Retrieved subject should match"
    assert retrieved_session.notes == session.notes, "Retrieved notes should match"
    
    # Test listing
    sessions = db_manager.get_study_sessions()
    assert len(sessions) > 0, "Should have at least one study session"
    
    # Test filtering by subject
    test_sessions = db_manager.get_study_sessions(subject="Test Subject")
    assert len(test_sessions) >= 1, "Should find the test session by subject"
    
    # Test update
    session.notes = "Updated test notes"
    success = db_manager.update_study_session(session)
    assert success, "Should be able to update study session"
    
    updated_session = db_manager.get_study_session(session.id)
    assert updated_session.notes == "Updated test notes", "Notes should be updated"
    
    # Test deletion
    success = db_manager.delete_study_session(session.id)
    assert success, "Should be able to delete study session"
    
    deleted_session = db_manager.get_study_session(session.id)
    assert deleted_session is None, "Session should be deleted"
    
    print("✓ Database Integration tests passed")


def test_study_session_model():
    """Test StudySession model functionality"""
    print("Testing StudySession Model...")
    
    # Test active session
    session = StudySession(subject="Physics")
    assert session.is_active, "New session should be active"
    assert session.duration >= 0, "Duration should be non-negative"
    
    # Test ending session
    session.end_session("Completed mechanics chapter")
    assert not session.is_active, "Ended session should not be active"
    assert session.notes == "Completed mechanics chapter", "Notes should be set"
    assert session.end_time is not None, "End time should be set"
    
    # Test task completion tracking
    session.add_completed_task("task_1")
    session.add_completed_task("task_2")
    assert len(session.tasks_completed) == 2, "Should have 2 completed tasks"
    assert "task_1" in session.tasks_completed, "Should contain task_1"
    
    session.remove_completed_task("task_1")
    assert len(session.tasks_completed) == 1, "Should have 1 completed task after removal"
    assert "task_1" not in session.tasks_completed, "Should not contain task_1"
    
    # Test formatted duration
    formatted = session.get_formatted_duration()
    assert "m" in formatted, "Formatted duration should contain minutes"
    
    # Test serialization
    session_dict = session.to_dict()
    assert 'id' in session_dict, "Dictionary should contain id"
    assert 'subject' in session_dict, "Dictionary should contain subject"
    assert 'start_time' in session_dict, "Dictionary should contain start_time"
    
    # Test deserialization
    restored_session = StudySession.from_dict(session_dict)
    assert restored_session.subject == session.subject, "Subject should be restored"
    assert restored_session.notes == session.notes, "Notes should be restored"
    
    print("✓ StudySession Model tests passed")


def main():
    """Run all tests"""
    print("Running StudyTracker Simple Tests...\n")
    
    try:
        test_study_session_model()
        test_pomodoro_timer()
        test_study_stats()
        test_study_goals()
        test_database_integration()
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)