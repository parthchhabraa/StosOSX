"""
Verification script for database integration with StosOS models.
"""

import os
import sys
import tempfile
import shutil

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment to prevent Kivy window creation
os.environ['KIVY_NO_CONSOLELOG'] = '1'
os.environ['KIVY_NO_ARGS'] = '1'


def verify_database_integration():
    """Verify database integration works correctly."""
    print("Verifying StosOS Database Integration")
    print("=" * 40)
    
    verification_results = []
    
    try:
        # Test 1: Import models without Kivy interference
        print("\n1. Testing model imports...")
        try:
            from models.task import Task, Priority
            from models.idea import Idea
            from models.study_session import StudySession
            from models.smart_device import SmartDevice, DeviceType, Platform
            print("✓ All models imported successfully")
            verification_results.append(("Model Imports", True))
        except Exception as e:
            print(f"❌ Model import failed: {e}")
            verification_results.append(("Model Imports", False))
            return verification_results
        
        # Test 2: Test model creation and validation
        print("\n2. Testing model creation...")
        try:
            # Create instances of each model
            task = Task(title="Test Task", priority=Priority.HIGH)
            idea = Idea(content="Test idea", tags=["test"])
            session = StudySession(subject="Physics")
            device = SmartDevice(
                name="Test Device",
                device_type=DeviceType.LIGHT,
                platform=Platform.GOOGLE
            )
            
            print("✓ All models created successfully")
            verification_results.append(("Model Creation", True))
        except Exception as e:
            print(f"❌ Model creation failed: {e}")
            verification_results.append(("Model Creation", False))
        
        # Test 3: Test model serialization
        print("\n3. Testing model serialization...")
        try:
            # Test serialization for each model
            task_dict = task.to_dict()
            restored_task = Task.from_dict(task_dict)
            assert restored_task.title == task.title
            
            idea_dict = idea.to_dict()
            restored_idea = Idea.from_dict(idea_dict)
            assert restored_idea.content == idea.content
            
            session_dict = session.to_dict()
            restored_session = StudySession.from_dict(session_dict)
            assert restored_session.subject == session.subject
            
            device_dict = device.to_dict()
            restored_device = SmartDevice.from_dict(device_dict)
            assert restored_device.name == device.name
            
            print("✓ All model serialization works")
            verification_results.append(("Model Serialization", True))
        except Exception as e:
            print(f"❌ Model serialization failed: {e}")
            verification_results.append(("Model Serialization", False))
        
        # Test 4: Test database manager import
        print("\n4. Testing database manager import...")
        try:
            from core.database_manager import DatabaseManager
            print("✓ Database manager imported successfully")
            verification_results.append(("Database Manager Import", True))
        except Exception as e:
            print(f"❌ Database manager import failed: {e}")
            verification_results.append(("Database Manager Import", False))
            return verification_results
        
        # Test 5: Test database initialization
        print("\n5. Testing database initialization...")
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_stosos.db")
        
        try:
            db = DatabaseManager(db_path)
            
            # Verify database file exists
            assert os.path.exists(db_path)
            
            # Verify tables exist
            stats = db.get_database_stats()
            required_tables = ['tasks', 'ideas', 'study_sessions', 'smart_devices', 'settings']
            for table in required_tables:
                assert table in stats
            
            print("✓ Database initialized with all required tables")
            verification_results.append(("Database Initialization", True))
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            verification_results.append(("Database Initialization", False))
        finally:
            try:
                db.close_connections()
            except:
                pass
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        # Test 6: Test basic CRUD operations
        print("\n6. Testing basic CRUD operations...")
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_crud.db")
        
        try:
            db = DatabaseManager(db_path)
            
            # Test task operations
            test_task = Task(title="CRUD Test Task", category="Testing")
            assert db.create_task(test_task)
            
            retrieved_task = db.get_task(test_task.id)
            assert retrieved_task is not None
            assert retrieved_task.title == test_task.title
            
            test_task.completed = True
            assert db.update_task(test_task)
            
            updated_task = db.get_task(test_task.id)
            assert updated_task.completed
            
            assert db.delete_task(test_task.id)
            deleted_task = db.get_task(test_task.id)
            assert deleted_task is None
            
            print("✓ CRUD operations work correctly")
            verification_results.append(("CRUD Operations", True))
            
        except Exception as e:
            print(f"❌ CRUD operations failed: {e}")
            verification_results.append(("CRUD Operations", False))
        finally:
            try:
                db.close_connections()
            except:
                pass
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        # Test 7: Test settings operations
        print("\n7. Testing settings operations...")
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_settings.db")
        
        try:
            db = DatabaseManager(db_path)
            
            # Test setting operations
            assert db.set_setting("test_key", "test_value")
            
            value = db.get_setting("test_key")
            assert value == "test_value"
            
            default_value = db.get_setting("non_existent", "default")
            assert default_value == "default"
            
            print("✓ Settings operations work correctly")
            verification_results.append(("Settings Operations", True))
            
        except Exception as e:
            print(f"❌ Settings operations failed: {e}")
            verification_results.append(("Settings Operations", False))
        finally:
            try:
                db.close_connections()
            except:
                pass
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"\n❌ Unexpected error during verification: {e}")
        import traceback
        traceback.print_exc()
        verification_results.append(("Unexpected Error", False))
    
    return verification_results


def print_verification_summary(results):
    """Print verification summary."""
    print("\n" + "=" * 40)
    print("VERIFICATION SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if success:
            passed += 1
    
    print("-" * 40)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All database integration tests passed!")
        print("The database system is ready for use.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("Please review the errors above.")
        return False


if __name__ == "__main__":
    results = verify_database_integration()
    success = print_verification_summary(results)
    
    if not success:
        sys.exit(1)