#!/usr/bin/env python3
"""
Demo script for Idea Board Module

Demonstrates the idea board functionality including:
- Creating and managing ideas
- Tag system
- Search and filtering
- Export functionality
"""

import sys
import os
import tempfile
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.idea import Idea
from core.database_manager import DatabaseManager


def demo_idea_management():
    """Demonstrate idea management functionality"""
    print("🚀 StosOS Idea Board Demo")
    print("=" * 50)
    
    # Create temporary database for demo
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_db:
        db_path = tmp_db.name
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        db_manager = DatabaseManager(db_path)
        
        # Create sample ideas
        print("\n💡 Creating sample ideas...")
        
        sample_ideas = [
            Idea(
                content="Quantum computing algorithm for solving NP-complete problems faster",
                tags=["quantum", "algorithms", "complexity", "research"]
            ),
            Idea(
                content="Machine learning model to predict student performance in IIT-JEE",
                tags=["ml", "education", "prediction", "iit-jee"]
            ),
            Idea(
                content="Renewable energy storage using advanced battery chemistry",
                tags=["energy", "battery", "chemistry", "sustainability"]
            ),
            Idea(
                content="Smart home automation system with voice control and AI",
                tags=["iot", "ai", "automation", "smart-home"]
            ),
            Idea(
                content="Physics simulation engine for educational purposes",
                tags=["physics", "simulation", "education", "software"]
            ),
            Idea(
                content="Blockchain-based academic credential verification system",
                tags=["blockchain", "education", "verification", "security"]
            )
        ]
        
        # Save ideas to database
        for i, idea in enumerate(sample_ideas, 1):
            if db_manager.create_idea(idea):
                print(f"  ✓ Idea {i}: {idea.content[:50]}...")
            else:
                print(f"  ❌ Failed to save idea {i}")
        
        # Demonstrate retrieval and filtering
        print(f"\n📋 Total ideas in database: {len(db_manager.get_ideas())}")
        
        # Filter by tags
        print("\n🏷️  Filtering by tags:")
        
        education_ideas = db_manager.get_ideas(tag="education")
        print(f"  📚 Education-related ideas: {len(education_ideas)}")
        for idea in education_ideas:
            print(f"    - {idea.content[:60]}...")
        
        research_ideas = db_manager.get_ideas(tag="research")
        print(f"  🔬 Research ideas: {len(research_ideas)}")
        for idea in research_ideas:
            print(f"    - {idea.content[:60]}...")
        
        # Search by content
        print("\n🔍 Searching by content:")
        
        ai_ideas = db_manager.get_ideas(search_term="AI")
        print(f"  🤖 Ideas mentioning 'AI': {len(ai_ideas)}")
        for idea in ai_ideas:
            print(f"    - {idea.content[:60]}...")
        
        physics_ideas = db_manager.get_ideas(search_term="physics")
        print(f"  ⚛️  Ideas mentioning 'physics': {len(physics_ideas)}")
        for idea in physics_ideas:
            print(f"    - {idea.content[:60]}...")
        
        # Demonstrate idea editing
        print("\n✏️  Demonstrating idea editing:")
        
        first_idea = sample_ideas[0]
        original_content = first_idea.content
        first_idea.update_content(original_content + " - Updated with new insights!")
        first_idea.add_tag("breakthrough")
        
        if db_manager.update_idea(first_idea):
            print(f"  ✓ Updated idea: {first_idea.content[:60]}...")
            print(f"  ✓ Added tag 'breakthrough': {first_idea.tags}")
        
        # Demonstrate export functionality
        print("\n📤 Demonstrating export functionality:")
        
        # Export single idea as markdown
        def generate_markdown_export(idea):
            content = f"# Idea: {idea.content[:50]}{'...' if len(idea.content) > 50 else ''}\n\n"
            content += f"**Created:** {idea.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"**Updated:** {idea.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if idea.tags:
                content += f"**Tags:** {', '.join(f'#{tag}' for tag in idea.tags)}\n\n"
            
            content += "## Content\n\n"
            content += idea.content + "\n\n"
            
            content += "---\n"
            content += f"*Exported from StosOS Idea Board on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
            
            return content
        
        markdown_export = generate_markdown_export(first_idea)
        print("  📝 Markdown export sample:")
        print("    " + "\n    ".join(markdown_export.split('\n')[:10]))
        print("    ...")
        
        # Export collection
        def generate_collection_export(ideas):
            content = f"# StosOS Ideas Collection\n\n"
            content += f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            content += f"**Total Ideas:** {len(ideas)}\n\n"
            
            for i, idea in enumerate(ideas, 1):
                content += f"## Idea {i}\n\n"
                content += f"**Tags:** {', '.join(f'#{tag}' for tag in idea.tags)}\n\n"
                content += idea.content + "\n\n"
                content += "---\n\n"
            
            return content
        
        collection_export = generate_collection_export(sample_ideas[:3])
        print("\n  📚 Collection export sample (first 3 ideas):")
        print("    " + "\n    ".join(collection_export.split('\n')[:15]))
        print("    ...")
        
        # Statistics
        print(f"\n📊 Statistics:")
        all_ideas = db_manager.get_ideas()
        
        # Count unique tags
        all_tags = set()
        for idea in all_ideas:
            all_tags.update(idea.tags)
        
        # Recent ideas (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_ideas = [idea for idea in all_ideas if idea.created_at >= recent_cutoff]
        
        print(f"  📝 Total ideas: {len(all_ideas)}")
        print(f"  🏷️  Unique tags: {len(all_tags)}")
        print(f"  🕐 Recent ideas (24h): {len(recent_ideas)}")
        print(f"  📊 Average tags per idea: {sum(len(idea.tags) for idea in all_ideas) / len(all_ideas):.1f}")
        
        # Most common tags
        tag_counts = {}
        for idea in all_ideas:
            for tag in idea.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"  🔥 Most popular tags:")
        for tag, count in popular_tags:
            print(f"    #{tag}: {count} ideas")
        
        print("\n" + "=" * 50)
        print("✅ Idea Board Demo Complete!")
        print("\nKey Features Demonstrated:")
        print("  💡 Quick idea capture with tags")
        print("  🔍 Search and filtering by content/tags")
        print("  ✏️  Idea editing and updating")
        print("  📤 Export to multiple formats")
        print("  📊 Statistics and analytics")
        print("  🏷️  Tag-based organization")
        
        print(f"\nThe Idea Board module is ready for integration into StosOS!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    return True


if __name__ == "__main__":
    success = demo_idea_management()
    sys.exit(0 if success else 1)