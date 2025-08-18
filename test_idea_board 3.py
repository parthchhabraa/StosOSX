#!/usr/bin/env python3
"""
Test script for Idea Board Module

Tests the idea board functionality including:
- Module initialization
- Idea creation and management
- Tag system
- Search and filtering
- Export functionality
"""

import sys
import os
import tempfile
import shutil
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.idea_board import IdeaBoard
from models.idea import Idea
from core.database_manager import DatabaseManager


def test_idea_model():
    """Test the Idea model functionality"""
    print("Testing Idea model...")
    
    # Test basic idea creation
    idea = Idea(
        content="Test idea for quantum computing research",
        tags=["physics", "quantum", "research"]
    )
    
    assert idea.content == "Test idea for quantum computing research"
    assert "physics" in idea.tags
    assert "quantum" in idea.tags
    assert "research" in idea.tags
    assert len(idea.tags) == 3
    
    # Test tag operations
    idea.add_tag("experiment")
    assert "experiment" in idea.tags
    assert len(idea.tags) == 4
    
    idea.remove_tag("physics")
    assert "physics" not in idea.tags
    assert len(idea.tags) == 3
    
    # Test content update
    original_updated = idea.updated_at
    idea.update_content("Updated quantum computing research idea")
    assert idea.content == "Updated quantum computing research idea"
    assert idea.updated_at > original_updated
    
    # Test serialization
    idea_dict = idea.to_dict()
    assert idea_dict['content'] == idea.content
    assert idea_dict['id'] == idea.id
    
    # Test deserialization
    restored_idea = Idea.from_dict(idea_dict)
    assert restored_idea.content == idea.content
    assert restored_idea.id == idea.id
    assert restored_idea.tags == idea.tags
    
    print("✓ Idea model tests passed")


def test_database_operations():
    """Test database operations for ideas"""
    print("Testing database operations...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        db_manager = DatabaseManager(db_path)
        
        # Test idea creation
        idea1 = Idea(
            content="First test idea about machine learning",
            tags=["ai", "ml", "research"]
        )
        
        idea2 = Idea(
            content="Second idea about renewable energy",
            tags=["energy", "sustainability", "research"]
        )
        
        # Create ideas in database
        assert db_manager.create_idea(idea1) == True
        assert db_manager.create_idea(idea2) == True
        
        # Test retrieval
        retrieved_idea = db_manager.get_idea(idea1.id)
        assert retrieved_idea is not None
        assert retrieved_idea.content == idea1.content
        assert retrieved_idea.tags == idea1.tags
        
        # Test get all ideas
        all_ideas = db_manager.get_ideas()
        assert len(all_ideas) == 2
        
        # Test search by tag
        research_ideas = db_manager.get_ideas(tag="research")
        assert len(research_ideas) == 2
        
        ai_ideas = db_manager.get_ideas(tag="ai")
        assert len(ai_ideas) == 1
        assert ai_ideas[0].content == idea1.content
        
        # Test search by content
        ml_ideas = db_manager.get_ideas(search_term="machine")
        assert len(ml_ideas) == 1
        assert ml_ideas[0].content == idea1.content
        
        # Test update
        idea1.update_content("Updated machine learning research idea")
        assert db_manager.update_idea(idea1) == True
        
        updated_idea = db_manager.get_idea(idea1.id)
        assert updated_idea.content == "Updated machine learning research idea"
        
        # Test deletion
        assert db_manager.delete_idea(idea2.id) == True
        
        remaining_ideas = db_manager.get_ideas()
        assert len(remaining_ideas) == 1
        assert remaining_ideas[0].id == idea1.id
        
        print("✓ Database operations tests passed")
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_idea_board_module():
    """Test the IdeaBoard module"""
    print("Testing IdeaBoard module...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Initialize module
        idea_board = IdeaBoard()
        
        # Override database path for testing
        idea_board.db_manager = DatabaseManager(db_path)
        
        # Test initialization
        assert idea_board.initialize() == True
        assert idea_board._initialized == True
        assert idea_board.module_id == "idea_board"
        assert idea_board.display_name == "Idea Board"
        
        # Test initial state
        assert len(idea_board.ideas) == 0
        assert len(idea_board.filtered_ideas) == 0
        
        # Add some test ideas
        test_ideas = [
            Idea(content="Physics research on quantum entanglement", tags=["physics", "quantum", "research"]),
            Idea(content="Math problem solving techniques", tags=["math", "problem-solving"]),
            Idea(content="Chemistry experiment with catalysts", tags=["chemistry", "experiment"]),
            Idea(content="Physics and math integration project", tags=["physics", "math", "project"])
        ]
        
        for idea in test_ideas:
            idea_board.db_manager.create_idea(idea)
        
        # Reload ideas
        idea_board._load_ideas()
        assert len(idea_board.ideas) == 4
        
        # Test filtering by tag
        idea_board.current_filter["tag"] = "physics"
        idea_board._apply_filters_and_sort()
        assert len(idea_board.filtered_ideas) == 2
        
        # Test search
        idea_board.current_filter["tag"] = None
        idea_board.search_term = "math"
        idea_board._apply_filters_and_sort()
        assert len(idea_board.filtered_ideas) == 2
        
        # Test sorting
        idea_board.search_term = ""
        idea_board.current_sort = "content"
        idea_board._apply_filters_and_sort()
        assert idea_board.filtered_ideas[0].content.startswith("Chemistry")
        
        # Test voice commands
        assert idea_board.handle_voice_command("new idea") == True
        assert idea_board.handle_voice_command("search physics") == True
        assert idea_board.handle_voice_command("export all") == True
        assert idea_board.handle_voice_command("random command") == False
        
        print("✓ IdeaBoard module tests passed")
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)


def test_export_functionality():
    """Test export functionality"""
    print("Testing export functionality...")
    
    # Create temporary database and export directory
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    export_dir = tempfile.mkdtemp()
    
    try:
        # Initialize module
        idea_board = IdeaBoard()
        idea_board.db_manager = DatabaseManager(db_path)
        idea_board.initialize()
        
        # Create test idea
        test_idea = Idea(
            content="Test idea for export functionality with detailed content",
            tags=["test", "export", "functionality"]
        )
        
        # Test markdown export
        markdown_content = idea_board._generate_markdown_content(test_idea)
        assert "# Idea:" in markdown_content
        assert test_idea.content in markdown_content
        assert "#test" in markdown_content
        assert "**Created:**" in markdown_content
        
        # Test text export
        text_content = idea_board._generate_text_content(test_idea)
        assert "IDEA:" in text_content
        assert test_idea.content in text_content
        assert "test, export, functionality" in text_content
        
        # Test JSON export
        json_content = idea_board._generate_json_content(test_idea)
        assert test_idea.id in json_content
        assert test_idea.content in json_content
        assert "export_info" in json_content
        
        # Test collection export
        ideas = [test_idea, Idea(content="Second idea", tags=["second"])]
        collection_content = idea_board._generate_markdown_collection(ideas)
        assert "# StosOS Ideas Collection" in collection_content
        assert "## Table of Contents" in collection_content
        assert test_idea.content in collection_content
        assert "Second idea" in collection_content
        
        print("✓ Export functionality tests passed")
        
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
        if os.path.exists(export_dir):
            shutil.rmtree(export_dir)


def run_all_tests():
    """Run all tests"""
    print("Running Idea Board Module Tests")
    print("=" * 50)
    
    try:
        test_idea_model()
        test_database_operations()
        test_idea_board_module()
        test_export_functionality()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        print("\nIdea Board Module is ready for use.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)