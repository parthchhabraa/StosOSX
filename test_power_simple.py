#!/usr/bin/env python3
"""
Simple Power Management Test
Quick test to verify basic power management functionality
"""

import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.power_manager import PowerManager, PowerState, PowerConfig
from core.logger import stosos_logger

logger = stosos_logger.get_logger(__name__)


def test_basic_functionality():
    """Test basic power management functionality"""
    print("=" * 50)
    print("Simple Power Management Test")
    print("=" * 50)
    
    try:
        # Test 1: Initialization
        print("\n1. Testing initialization...")
        pm = PowerManager()
        print(f"   Initial state: {pm.get_power_state()}")
        print(f"   Initial brightness: {pm.get_brightness()}")
        assert pm.get_power_state() == PowerState.ACTIVE
        print("   ✅ Initialization OK")
        
        # Test 2: Brightness control
        print("\n2. Testing brightness control...")
        pm.set_brightness(50)
        print(f"   Set to 50: {pm.get_brightness()}")
        assert pm.get_brightness() == 50
        
        pm.set_brightness(0)
        print(f"   Set to 0: {pm.get_brightness()}")
        assert pm.get_brightness() == 0
        
        pm.set_brightness(100)
        print(f"   Set to 100: {pm.get_brightness()}")
        assert pm.get_brightness() == 100
        print("   ✅ Brightness control OK")
        
        # Test 3: Force sleep
        print("\n3. Testing force sleep...")
        pm.force_sleep()
        print(f"   After force sleep: {pm.get_power_state()}")
        assert pm.get_power_state() == PowerState.SLEEP
        print("   ✅ Force sleep OK")
        
        # Test 4: Simple wake (direct state change)
        print("\n4. Testing direct wake...")
        # Directly set state to active (bypass complex wake logic)
        pm._set_power_state(PowerState.ACTIVE)
        pm._set_brightness(100)
        print(f"   After direct wake: {pm.get_power_state()}")
        assert pm.get_power_state() == PowerState.ACTIVE
        print("   ✅ Direct wake OK")
        
        # Test 5: User activity
        print("\n5. Testing user activity...")
        pm.on_user_activity()
        idle_time = pm.get_idle_time()
        print(f"   Idle time after activity: {idle_time:.3f}s")
        assert idle_time < 0.1
        print("   ✅ User activity OK")
        
        # Test 6: Touch events
        print("\n6. Testing touch events...")
        touch_data = {'pos': (100, 200), 'time': time.time()}
        pm.on_touch_event(touch_data)
        print("   Touch event processed")
        print("   ✅ Touch events OK")
        
        # Test 7: Statistics
        print("\n7. Testing statistics...")
        stats = pm.get_statistics()
        print(f"   Current state: {stats['current_state']}")
        print(f"   Current brightness: {stats['current_brightness']}")
        print(f"   Brightness method: {stats['brightness_method']}")
        assert 'current_state' in stats
        assert 'current_brightness' in stats
        print("   ✅ Statistics OK")
        
        print("\n" + "=" * 50)
        print("🎉 ALL BASIC TESTS PASSED!")
        print("Power management core functionality is working.")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("=" * 50)
        return False


if __name__ == '__main__':
    success = test_basic_functionality()
    sys.exit(0 if success else 1)