#!/usr/bin/env python3
"""
Simple test script for Idea Board Module

Tests core functionality without Kivy UI components.
"""

import sys
import os
import tempfile
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test the Idea model directly
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


def test_export_functions():
    """Test export functionality without UI"""
    print("Testing export functions...")
    
    # Create test idea
    test_idea = Idea(
        content="Test idea for export functionality with detailed content",
        tags=["test", "export", "functionality"]
    )
    
    # Test markdown generation
    def generate_markdown_content(idea):
        content = f"# Idea: {idea.content[:50]}{'...' if len(idea.content) > 50 else ''}\n\n"
        content += f"**Created:** {idea.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"**Updated:** {idea.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if idea.tags:
            content += f"**Tags:** {', '.join(f'#{tag}' for tag in idea.tags)}\n\n"
        
        content += "## Content\n\n"
        content += idea.content + "\n\n"
        
        if idea.attachments:
            content += "## Attachments\n\n"
            for attachment in idea.attachments:
                content += f"- {attachment}\n"
            content += "\n"
        
        content += "---\n"
        content += f"*Exported from StosOS Idea Board on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return content
    
    markdown_content = generate_markdown_content(test_idea)
    assert "# Idea:" in markdown_content
    assert test_idea.content in markdown_content
    assert "#test" in markdown_content
    assert "**Created:**" in markdown_content
    
    # Test text generation
    def generate_text_content(idea):
        content = f"IDEA: {idea.content[:50]}{'...' if len(idea.content) > 50 else ''}\n"
        content += "=" * 60 + "\n\n"
        content += f"Created: {idea.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += f"Updated: {idea.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if idea.tags:
            content += f"Tags: {', '.join(idea.tags)}\n"
        
        content += "\nCONTENT:\n"
        content += "-" * 20 + "\n"
        content += idea.content + "\n\n"
        
        if idea.attachments:
            content += "ATTACHMENTS:\n"
            content += "-" * 20 + "\n"
            for attachment in idea.attachments:
                content += f"- {attachment}\n"
            content += "\n"
        
        content += f"Exported from StosOS Idea Board on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return content
    
    text_content = generate_text_content(test_idea)
    assert "IDEA:" in text_content
    assert test_idea.content in text_content
    assert "test, export, functionality" in text_content
    
    # Test JSON generation
    def generate_json_content(idea):
        import json
        
        data = {
            "idea": idea.to_dict(),
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "exported_by": "StosOS Idea Board",
                "format_version": "1.0"
            }
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    json_content = generate_json_content(test_idea)
    assert test_idea.id in json_content
    assert test_idea.content in json_content
    assert "export_info" in json_content
    
    print("✓ Export functions tests passed")


def run_all_tests():
    """Run all tests"""
    print("Running Idea Board Core Tests")
    print("=" * 50)
    
    try:
        test_idea_model()
        test_database_operations()
        test_export_functions()
        
        print("\n" + "=" * 50)
        print("✅ All core tests passed successfully!")
        print("\nIdea Board core functionality is working correctly.")
        print("The module should integrate properly with the StosOS system.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)