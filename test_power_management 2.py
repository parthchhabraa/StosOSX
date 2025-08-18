#!/usr/bin/env python3
"""
Test Power Management System
Comprehensive testing for PowerManager functionality
"""

import sys
import time
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.power_manager import PowerManager, PowerState, PowerConfig
from core.logger import stosos_logger

logger = stosos_logger.get_logger(__name__)


class PowerManagementTester:
    """Test suite for power management functionality"""
    
    def __init__(self):
        self.test_results = []
        self.power_manager = None
    
    def run_all_tests(self):
        """Run comprehensive power management tests"""
        print("=" * 60)
        print("StosOS Power Management Test Suite")
        print("=" * 60)
        
        try:
            # Test 1: Basic initialization
            self.test_initialization()
            
            # Test 2: Power state transitions
            self.test_power_state_transitions()
            
            # Test 3: Brightness control
            self.test_brightness_control()
            
            # Test 4: Idle detection
            self.test_idle_detection()
            
            # Test 5: Touch event handling
            self.test_touch_events()
            
            # Test 6: Wake functionality
            self.test_wake_functionality()
            
            # Test 7: Configuration handling
            self.test_configuration()
            
            # Test 8: Statistics and monitoring
            self.test_statistics()
            
            # Test 9: Error handling
            self.test_error_handling()
            
            # Test 10: Threading safety
            self.test_threading_safety()
            
        except Exception as e:
            logger.error(f"Test suite error: {e}")
            self.test_results.append(("Test Suite", False, str(e)))
        
        finally:
            # Cleanup
            if self.power_manager:
                self.power_manager.stop_monitoring()
        
        # Print results
        self.print_test_results()
    
    def test_initialization(self):
        """Test PowerManager initialization"""
        test_name = "PowerManager Initialization"
        try:
            print(f"\n🔧 Testing {test_name}...")
            
            # Test with default config
            self.power_manager = PowerManager()
            assert self.power_manager.current_state == PowerState.ACTIVE
            assert self.power_manager.current_brightness == 100
            
            # Test with custom config
            custom_config = PowerConfig(
                dim_timeout=15.0,
                sleep_timeout=30.0,
                active_brightness=90,
                dimmed_brightness=15
            )
            
            pm_custom = PowerManager(custom_config)
            assert pm_custom.config.dim_timeout == 15.0
            assert pm_custom.config.active_brightness == 90
            
            self.test_results.append((test_name, True, "Initialization successful"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_power_state_transitions(self):
        """Test power state transitions"""
        test_name = "Power State Transitions"
        try:
            print(f"\n🔄 Testing {test_name}...")
            
            # Test manual state changes
            initial_state = self.power_manager.get_power_state()
            print(f"  Initial state: {initial_state}")
            assert initial_state == PowerState.ACTIVE, f"Expected ACTIVE, got {initial_state}"
            
            # Test wake display (should stay active if already active)
            self.power_manager.wake_display("test")
            current_state = self.power_manager.get_power_state()
            print(f"  After wake (already active): {current_state}")
            assert current_state == PowerState.ACTIVE, f"Expected ACTIVE, got {current_state}"
            
            # Test force sleep
            self.power_manager.force_sleep()
            sleep_state = self.power_manager.get_power_state()
            print(f"  After force sleep: {sleep_state}")
            assert sleep_state == PowerState.SLEEP, f"Expected SLEEP, got {sleep_state}"
            
            # Test wake from sleep
            print("  Calling wake_display...")
            self.power_manager.wake_display("test")
            print("  Wake_display called, waiting for transition...")
            
            # Wait for wake transition with timeout
            max_wait = 2.0
            wait_time = 0.0
            while wait_time < max_wait:
                wake_state = self.power_manager.get_power_state()
                print(f"  Current state after {wait_time:.1f}s: {wake_state}")
                if wake_state == PowerState.ACTIVE:
                    break
                time.sleep(0.1)
                wait_time += 0.1
            
            final_state = self.power_manager.get_power_state()
            print(f"  Final state after wake: {final_state}")
            assert final_state == PowerState.ACTIVE, f"Expected ACTIVE, got {final_state}"
            
            self.test_results.append((test_name, True, "State transitions working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_brightness_control(self):
        """Test brightness control functionality"""
        test_name = "Brightness Control"
        try:
            print(f"\n💡 Testing {test_name}...")
            
            # Test brightness setting
            original_brightness = self.power_manager.get_brightness()
            print(f"  Original brightness: {original_brightness}")
            
            # Test valid brightness values
            self.power_manager.set_brightness(50)
            brightness_50 = self.power_manager.get_brightness()
            print(f"  Set to 50, got: {brightness_50}")
            assert brightness_50 == 50, f"Expected 50, got {brightness_50}"
            
            self.power_manager.set_brightness(0)
            brightness_0 = self.power_manager.get_brightness()
            print(f"  Set to 0, got: {brightness_0}")
            assert brightness_0 == 0, f"Expected 0, got {brightness_0}"
            
            self.power_manager.set_brightness(100)
            brightness_100 = self.power_manager.get_brightness()
            print(f"  Set to 100, got: {brightness_100}")
            assert brightness_100 == 100, f"Expected 100, got {brightness_100}"
            
            # Test boundary values
            self.power_manager.set_brightness(-10)  # Should clamp to 0
            brightness_neg = self.power_manager.get_brightness()
            print(f"  Set to -10, got: {brightness_neg}")
            assert brightness_neg == 0, f"Expected 0 (clamped), got {brightness_neg}"
            
            self.power_manager.set_brightness(150)  # Should clamp to 100
            brightness_over = self.power_manager.get_brightness()
            print(f"  Set to 150, got: {brightness_over}")
            assert brightness_over == 100, f"Expected 100 (clamped), got {brightness_over}"
            
            # Restore original brightness
            self.power_manager.set_brightness(original_brightness)
            
            self.test_results.append((test_name, True, "Brightness control working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_idle_detection(self):
        """Test idle time detection"""
        test_name = "Idle Detection"
        try:
            print(f"\n⏱️ Testing {test_name}...")
            
            # Reset activity time
            self.power_manager.on_user_activity()
            initial_idle = self.power_manager.get_idle_time()
            
            # Wait a bit and check idle time increased
            time.sleep(1.1)
            new_idle = self.power_manager.get_idle_time()
            assert new_idle > initial_idle
            assert new_idle >= 1.0
            
            # Reset activity and check idle time resets
            self.power_manager.on_user_activity()
            reset_idle = self.power_manager.get_idle_time()
            assert reset_idle < 0.5  # Should be very small
            
            self.test_results.append((test_name, True, "Idle detection working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_touch_events(self):
        """Test touch event handling"""
        test_name = "Touch Event Handling"
        try:
            print(f"\n👆 Testing {test_name}...")
            
            # Test touch handler registration
            touch_events = []
            
            def test_touch_handler(touch_data):
                touch_events.append(touch_data)
            
            self.power_manager.register_touch_handler(test_touch_handler)
            
            # Simulate touch event
            test_touch_data = {
                'pos': (100, 200),
                'time': time.time(),
                'is_double_tap': False
            }
            
            self.power_manager.on_touch_event(test_touch_data)
            
            # Check handler was called
            assert len(touch_events) == 1
            assert touch_events[0] == test_touch_data
            
            # Test handler unregistration
            self.power_manager.unregister_touch_handler(test_touch_handler)
            self.power_manager.on_touch_event(test_touch_data)
            
            # Should still be 1 (handler not called again)
            assert len(touch_events) == 1
            
            self.test_results.append((test_name, True, "Touch events working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_wake_functionality(self):
        """Test wake functionality"""
        test_name = "Wake Functionality"
        try:
            print(f"\n🌅 Testing {test_name}...")
            
            # Test voice wake callback
            voice_wake_called = False
            
            def voice_wake_callback():
                nonlocal voice_wake_called
                voice_wake_called = True
                return True  # Simulate wake word detected
            
            self.power_manager.set_voice_wake_callback(voice_wake_callback)
            print("  Voice wake callback set")
            
            # Test network wake callback
            network_wake_called = False
            
            def network_wake_callback():
                nonlocal network_wake_called
                network_wake_called = True
                return False  # Simulate no network wake command
            
            self.power_manager.set_network_wake_callback(network_wake_callback)
            print("  Network wake callback set")
            
            # Put system to sleep
            self.power_manager.force_sleep()
            sleep_state = self.power_manager.get_power_state()
            print(f"  After force sleep: {sleep_state}")
            assert sleep_state == PowerState.SLEEP, f"Expected SLEEP, got {sleep_state}"
            
            # Test wake from different sources
            self.power_manager.wake_display("manual")
            time.sleep(0.2)
            wake_state = self.power_manager.get_power_state()
            print(f"  After manual wake: {wake_state}")
            assert wake_state == PowerState.ACTIVE, f"Expected ACTIVE, got {wake_state}"
            
            self.test_results.append((test_name, True, "Wake functionality working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_configuration(self):
        """Test configuration handling"""
        test_name = "Configuration Handling"
        try:
            print(f"\n⚙️ Testing {test_name}...")
            
            # Test config access
            config = self.power_manager.config
            assert hasattr(config, 'dim_timeout')
            assert hasattr(config, 'sleep_timeout')
            assert hasattr(config, 'active_brightness')
            
            # Test config modification
            original_dim_timeout = config.dim_timeout
            config.dim_timeout = 45.0
            assert config.dim_timeout == 45.0
            
            # Restore original
            config.dim_timeout = original_dim_timeout
            
            self.test_results.append((test_name, True, "Configuration working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_statistics(self):
        """Test statistics and monitoring"""
        test_name = "Statistics and Monitoring"
        try:
            print(f"\n📊 Testing {test_name}...")
            
            # Get statistics
            stats = self.power_manager.get_statistics()
            
            # Check required fields
            required_fields = [
                'current_state', 'current_brightness', 'idle_time',
                'state_history', 'wake_events', 'brightness_method'
            ]
            
            for field in required_fields:
                assert field in stats, f"Missing field: {field}"
            
            # Check data types
            assert isinstance(stats['current_state'], str)
            assert isinstance(stats['current_brightness'], int)
            assert isinstance(stats['idle_time'], float)
            assert isinstance(stats['state_history'], list)
            assert isinstance(stats['wake_events'], list)
            
            self.test_results.append((test_name, True, "Statistics working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_error_handling(self):
        """Test error handling"""
        test_name = "Error Handling"
        try:
            print(f"\n🛡️ Testing {test_name}...")
            
            # Test invalid touch data handling
            print("  Testing invalid touch data...")
            self.power_manager.on_touch_event(None)  # Should not crash
            self.power_manager.on_touch_event({})    # Should not crash
            print("  Invalid touch data handled gracefully")
            
            # Test invalid brightness values (should be clamped)
            print("  Testing brightness clamping...")
            self.power_manager.set_brightness(-100)
            brightness_neg = self.power_manager.get_brightness()
            print(f"  Set -100, got: {brightness_neg}")
            assert brightness_neg == 0, f"Expected 0, got {brightness_neg}"
            
            self.power_manager.set_brightness(1000)
            brightness_over = self.power_manager.get_brightness()
            print(f"  Set 1000, got: {brightness_over}")
            assert brightness_over == 100, f"Expected 100, got {brightness_over}"
            
            self.test_results.append((test_name, True, "Error handling working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def test_threading_safety(self):
        """Test threading safety"""
        test_name = "Threading Safety"
        try:
            print(f"\n🧵 Testing {test_name}...")
            
            # Start monitoring
            self.power_manager.start_monitoring()
            time.sleep(0.5)  # Let monitoring start
            
            # Test concurrent operations
            def concurrent_operations():
                for i in range(10):
                    self.power_manager.on_user_activity()
                    self.power_manager.set_brightness(50 + (i % 50))
                    time.sleep(0.01)
            
            # Run multiple threads
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=concurrent_operations)
                threads.append(thread)
                thread.start()
            
            # Wait for completion
            for thread in threads:
                thread.join()
            
            # Stop monitoring
            self.power_manager.stop_monitoring()
            
            self.test_results.append((test_name, True, "Threading safety working"))
            print(f"✅ {test_name} - PASSED")
            
        except Exception as e:
            self.test_results.append((test_name, False, str(e)))
            print(f"❌ {test_name} - FAILED: {e}")
    
    def print_test_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, message in self.test_results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status:<10} {test_name:<30} {message}")
        
        print("-" * 60)
        print(f"TOTAL: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Power management system is working correctly.")
        else:
            print("⚠️  Some tests failed. Please review the implementation.")
        
        print("=" * 60)


def main():
    """Run power management tests"""
    tester = PowerManagementTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()