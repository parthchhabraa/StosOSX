#!/usr/bin/env python3
"""
Simple Smart Home Services Test

Tests the core smart home services without complex module dependencies.
"""

import sys
import os
import time
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import services directly
import importlib.util

# Import smart device model
spec = importlib.util.spec_from_file_location("smart_device", "models/smart_device.py")
smart_device_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smart_device_module)
SmartDevice = smart_device_module.SmartDevice
DeviceType = smart_device_module.DeviceType
Platform = smart_device_module.Platform

# Import Google Assistant service
spec = importlib.util.spec_from_file_location("google_assistant_service", "services/google_assistant_service.py")
google_service_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(google_service_module)
GoogleAssistantService = google_service_module.GoogleAssistantService

# Import Alexa service
spec = importlib.util.spec_from_file_location("alexa_service", "services/alexa_service.py")
alexa_service_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alexa_service_module)
AlexaService = alexa_service_module.AlexaService


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_device_info(device):
    """Print formatted device information"""
    status_icon = "🟢" if device.is_online else "🔴"
    platform_icon = "🔵" if device.platform == Platform.GOOGLE else "🟠"
    
    print(f"{status_icon} {platform_icon} {device.name}")
    print(f"   Type: {device.device_type.value} | Room: {device.room}")
    print(f"   Capabilities: {', '.join(device.capabilities)}")
    
    if device.status:
        status_items = []
        for key, value in device.status.items():
            status_items.append(f"{key}: {value}")
        print(f"   Status: {' | '.join(status_items)}")
    
    print(f"   Last Updated: {device.last_updated.strftime('%H:%M:%S')}")


def test_google_assistant_service():
    """Test Google Assistant service"""
    print_header("Google Assistant Service Test")
    
    print("🔵 Initializing Google Assistant Service...")
    service = GoogleAssistantService()
    
    print("🔵 Authenticating...")
    if service.authenticate():
        print("✅ Authentication successful")
        
        print("🔵 Discovering devices...")
        devices = service.get_devices()
        print(f"📱 Found {len(devices)} devices")
        
        for i, device in enumerate(devices[:3]):  # Show first 3 devices
            print(f"\n📱 Device {i+1}:")
            print_device_info(device)
        
        # Test device control
        if devices:
            device = devices[0]
            print(f"\n🔵 Testing device control on: {device.name}")
            
            print("   💡 Turning device on...")
            if service.control_device(device.id, "power_on"):
                print("   ✅ Power on successful")
                print_device_info(device)
            
            if device.has_capability("brightness"):
                print("   🔆 Setting brightness to 75%...")
                if service.control_device(device.id, "set_brightness", {"brightness": 75}):
                    print("   ✅ Brightness control successful")
                    print_device_info(device)
            
            time.sleep(0.5)
            
            print("   💡 Turning device off...")
            if service.control_device(device.id, "power_off"):
                print("   ✅ Power off successful")
                print_device_info(device)
        
        # Test connection
        print(f"\n🔵 Testing connection...")
        if service.test_connection():
            print("✅ Connection test passed")
        else:
            print("❌ Connection test failed")
        
        return True
    else:
        print("❌ Authentication failed")
        return False


def test_alexa_service():
    """Test Alexa service"""
    print_header("Alexa Service Test")
    
    print("🟠 Initializing Alexa Service...")
    service = AlexaService()
    
    print("🟠 Authenticating...")
    if service.authenticate():
        print("✅ Authentication successful")
        
        print("🟠 Discovering devices...")
        devices = service.get_devices()
        print(f"📱 Found {len(devices)} devices")
        
        for i, device in enumerate(devices[:3]):  # Show first 3 devices
            print(f"\n📱 Device {i+1}:")
            print_device_info(device)
        
        # Test device control
        if devices:
            device = devices[0]
            print(f"\n🟠 Testing device control on: {device.name}")
            
            print("   🔊 Turning device on...")
            if service.control_device(device.id, "power_on"):
                print("   ✅ Power on successful")
                print_device_info(device)
            
            if device.has_capability("volume"):
                print("   🔊 Setting volume to 60%...")
                if service.control_device(device.id, "set_volume", {"volume": 60}):
                    print("   ✅ Volume control successful")
                    print_device_info(device)
        
        # Test group control
        print(f"\n🟠 Testing group control...")
        groups = service.get_device_groups()
        print(f"🏠 Found {len(groups)} rooms: {list(groups.keys())}")
        
        if groups:
            room_name = list(groups.keys())[0]
            print(f"   🏠 Controlling all devices in '{room_name}'...")
            if service.control_group(room_name, "power_on"):
                print("   ✅ Group control successful")
            else:
                print("   ⚠️ Group control completed with some failures")
        
        # Test connection
        print(f"\n🟠 Testing connection...")
        if service.test_connection():
            print("✅ Connection test passed")
        else:
            print("❌ Connection test failed")
        
        return True
    else:
        print("❌ Authentication failed")
        return False


def test_device_callbacks():
    """Test device update callbacks"""
    print_header("Device Callback Test")
    
    print("📡 Testing device update callbacks...")
    
    # Initialize services
    google_service = GoogleAssistantService()
    alexa_service = AlexaService()
    
    # Callback tracking
    callback_count = 0
    updated_devices = []
    
    def device_callback(device):
        nonlocal callback_count, updated_devices
        callback_count += 1
        updated_devices.append(device)
        print(f"   📡 Callback #{callback_count}: {device.name} updated")
    
    # Authenticate and add callbacks
    google_auth = google_service.authenticate()
    alexa_auth = alexa_service.authenticate()
    
    if google_auth:
        google_service.add_device_callback(device_callback)
        print("✅ Google callback registered")
    
    if alexa_auth:
        alexa_service.add_device_callback(device_callback)
        print("✅ Alexa callback registered")
    
    # Trigger some device updates
    print("\n📡 Triggering device updates...")
    
    if google_auth:
        google_devices = google_service.get_devices()
        if google_devices:
            device = google_devices[0]
            print(f"   🔵 Updating Google device: {device.name}")
            google_service.control_device(device.id, "power_on")
            time.sleep(0.1)
            google_service.control_device(device.id, "power_off")
    
    if alexa_auth:
        alexa_devices = alexa_service.get_devices()
        if alexa_devices:
            device = alexa_devices[0]
            print(f"   🟠 Updating Alexa device: {device.name}")
            alexa_service.control_device(device.id, "power_on")
            time.sleep(0.1)
            alexa_service.control_device(device.id, "power_off")
    
    print(f"\n📊 Total callbacks received: {callback_count}")
    print(f"📊 Devices updated: {len(updated_devices)}")
    
    return callback_count > 0


def test_scene_simulation(google_service=None, alexa_service=None):
    """Test scene management simulation"""
    print_header("Scene Management Simulation")
    
    print("🎬 Simulating scene management...")
    
    # Use provided services or initialize new ones
    if not google_service:
        google_service = GoogleAssistantService()
        google_auth = google_service.authenticate()
    else:
        google_auth = google_service.is_authenticated()
        
    if not alexa_service:
        alexa_service = AlexaService()
        alexa_auth = alexa_service.authenticate()
    else:
        alexa_auth = alexa_service.is_authenticated()
    
    if not (google_auth or alexa_auth):
        print("❌ No services available for scene test")
        return False
    
    # Collect all devices
    all_devices = []
    if google_auth:
        all_devices.extend(google_service.get_devices())
    if alexa_auth:
        all_devices.extend(alexa_service.get_devices())
    
    if not all_devices:
        print("❌ No devices available for scene test")
        return False
    
    # Create a sample scene using actual device IDs
    scene_devices = {}
    for device in all_devices[:3]:  # Use first 3 devices
        if device.device_type.value == "LIGHT":
            scene_devices[device.id] = {
                "power": True,
                "brightness": 80
            }
        elif device.device_type.value == "SPEAKER":
            scene_devices[device.id] = {
                "power": True,
                "volume": 40
            }
        elif device.device_type.value == "THERMOSTAT":
            scene_devices[device.id] = {
                "target_temperature": 72
            }
        else:
            scene_devices[device.id] = {
                "power": True
            }
    
    sample_scene = {
        "name": "Study Mode",
        "description": "Optimal environment for studying",
        "devices": scene_devices
    }
    
    print(f"🎬 Scene: {sample_scene['name']}")
    print(f"   Description: {sample_scene['description']}")
    print(f"   Devices: {len(scene_devices)}")
    
    # Simulate scene activation
    print("\n🎬 Activating scene...")
    success_count = 0
    
    for device_id, settings in scene_devices.items():
        device = next((d for d in all_devices if d.id == device_id), None)
        if not device:
            print(f"   ⚠️ Device {device_id} not found")
            continue
        
        print(f"   📱 Configuring {device.name}...")
        
        # Apply settings
        for setting, value in settings.items():
            command = None
            parameters = None
            
            if setting == "power":
                command = "power_on" if value else "power_off"
            elif setting == "brightness" and "brightness" in device.capabilities:
                command = "set_brightness"
                parameters = {"brightness": value}
            elif setting == "volume" and "volume" in device.capabilities:
                command = "set_volume"
                parameters = {"volume": value}
            elif setting == "target_temperature" and "target_temperature" in device.capabilities:
                command = "set_temperature"
                parameters = {"temperature": value}
            else:
                print(f"      ⚠️ {setting} not supported by {device.name}")
                continue
            
            # Send command to appropriate service
            success = False
            try:
                if device.platform.value == "GOOGLE" and google_auth:
                    success = google_service.control_device(device_id, command, parameters)
                elif device.platform.value == "ALEXA" and alexa_auth:
                    success = alexa_service.control_device(device_id, command, parameters)
                
                if success:
                    success_count += 1
                    print(f"      ✅ {setting}: {value}")
                else:
                    print(f"      ❌ {setting}: {value}")
            except Exception as e:
                print(f"      ❌ {setting}: {value} (error: {e})")
    
    print(f"\n🎬 Scene activation completed: {success_count} settings applied")
    return success_count > 0


def test_requirements_compliance(google_service=None, alexa_service=None):
    """Test compliance with requirements"""
    print_header("Requirements Compliance Test")
    
    results = {}
    
    # Requirement 3.1: Display Google/Alexa devices
    print("🔍 Testing Requirement 3.1: Device Discovery and Display")
    
    # Use provided services or initialize new ones
    if not google_service:
        google_service = GoogleAssistantService()
        google_auth = google_service.authenticate()
    else:
        google_auth = google_service.is_authenticated()
        
    if not alexa_service:
        alexa_service = AlexaService()
        alexa_auth = alexa_service.authenticate()
    else:
        alexa_auth = alexa_service.is_authenticated()
    
    google_devices = google_service.get_devices() if google_auth else []
    alexa_devices = alexa_service.get_devices() if alexa_auth else []
    
    req_3_1 = len(google_devices) > 0 and len(alexa_devices) > 0
    results["3.1"] = req_3_1
    print(f"   {'✅' if req_3_1 else '❌'} Google: {len(google_devices)}, Alexa: {len(alexa_devices)} devices")
    
    # Requirement 3.2: Appropriate device controls
    print("\n🔍 Testing Requirement 3.2: Device Control Interfaces")
    all_devices = google_devices + alexa_devices
    control_types = set()
    
    for device in all_devices:
        # Check for specific control types
        if device.device_type.value == "LIGHT" and "brightness" in device.capabilities:
            control_types.add("light_brightness")
        if device.device_type.value == "SPEAKER" and "volume" in device.capabilities:
            control_types.add("speaker_volume")
        if device.device_type.value == "THERMOSTAT" and "target_temperature" in device.capabilities:
            control_types.add("thermostat_temperature")
        if "power" in device.capabilities:
            control_types.add("power_control")
    
    req_3_2 = len(control_types) >= 2  # At least 2 different control types
    results["3.2"] = req_3_2
    print(f"   {'✅' if req_3_2 else '❌'} Control types available: {list(control_types)}")
    
    # Requirement 3.3: Command execution within 2 seconds
    print("\n🔍 Testing Requirement 3.3: Command Response Time")
    if google_devices:
        device = google_devices[0]  # Use Google device specifically
        start_time = time.time()
        success = google_service.control_device(device.id, "power_on")
        response_time = time.time() - start_time
        req_3_3 = response_time < 2.0 and success
        results["3.3"] = req_3_3
        print(f"   {'✅' if req_3_3 else '❌'} Response time: {response_time:.3f}s (target: <2.0s)")
    elif alexa_devices:
        device = alexa_devices[0]  # Use Alexa device specifically
        start_time = time.time()
        success = alexa_service.control_device(device.id, "power_on")
        response_time = time.time() - start_time
        req_3_3 = response_time < 2.0 and success
        results["3.3"] = req_3_3
        print(f"   {'✅' if req_3_3 else '❌'} Response time: {response_time:.3f}s (target: <2.0s)")
    else:
        results["3.3"] = False
        print("   ❌ No devices available for testing")
    
    # Requirement 3.4: Real-time status updates
    print("\n🔍 Testing Requirement 3.4: Real-time Status Updates")
    callback_received = False
    
    def test_callback(device):
        nonlocal callback_received
        callback_received = True
    
    if google_auth:
        google_service.add_device_callback(test_callback)
    if alexa_auth:
        alexa_service.add_device_callback(test_callback)
    
    # Trigger an update
    if google_devices:
        device = google_devices[0]
        google_service.control_device(device.id, "power_off")
        time.sleep(0.1)  # Brief wait for callback
    elif alexa_devices:
        device = alexa_devices[0]
        alexa_service.control_device(device.id, "power_off")
        time.sleep(0.1)  # Brief wait for callback
    
    req_3_4 = callback_received
    results["3.4"] = req_3_4
    print(f"   {'✅' if req_3_4 else '❌'} Status update callback: {'received' if callback_received else 'not received'}")
    
    # Requirement 3.5: Scene management
    print("\n🔍 Testing Requirement 3.5: Scene Management")
    scene_test = test_scene_simulation(google_service, alexa_service)
    results["3.5"] = scene_test
    print(f"   {'✅' if scene_test else '❌'} Scene management: {'functional' if scene_test else 'not functional'}")
    
    # Summary
    print(f"\n📊 Requirements Summary:")
    passed = sum(results.values())
    total = len(results)
    
    for req, passed_test in results.items():
        print(f"   Requirement {req}: {'✅ PASS' if passed_test else '❌ FAIL'}")
    
    print(f"\n🎯 Overall: {passed}/{total} requirements met ({(passed/total)*100:.1f}%)")
    
    return passed == total


def main():
    """Main test function"""
    print("🏠 Smart Home Services Test")
    print("===========================")
    print("Testing core smart home functionality without complex dependencies")
    
    try:
        # Test individual services
        google_success = test_google_assistant_service()
        alexa_success = test_alexa_service()
        
        # Test callbacks
        callback_success = test_device_callbacks()
        
        # Initialize services for shared use
        google_service = GoogleAssistantService()
        alexa_service = AlexaService()
        google_service.authenticate()
        alexa_service.authenticate()
        
        # Test scene simulation
        scene_success = test_scene_simulation(google_service, alexa_service)
        
        # Test requirements compliance (pass services to avoid re-creating devices)
        requirements_success = test_requirements_compliance(google_service, alexa_service)
        
        print_header("Test Summary")
        
        tests = [
            ("Google Assistant Service", google_success),
            ("Alexa Service", alexa_success),
            ("Device Callbacks", callback_success),
            ("Scene Management", scene_success),
            ("Requirements Compliance", requirements_success)
        ]
        
        passed_count = sum(1 for _, success in tests if success)
        total_count = len(tests)
        
        print(f"Tests Passed: {passed_count}/{total_count}")
        
        for test_name, success in tests:
            print(f"   {'✅' if success else '❌'} {test_name}")
        
        if passed_count == total_count:
            print("\n🎉 All smart home functionality is working correctly!")
            print("   • Google Assistant SDK integration ✅")
            print("   • Alexa Voice Service integration ✅")
            print("   • Device discovery and control ✅")
            print("   • Real-time status updates ✅")
            print("   • Scene management ✅")
            print("   • All requirements met ✅")
        else:
            print(f"\n⚠️  {total_count - passed_count} test(s) failed")
            print("   Please check the failed components above")
        
        return passed_count == total_count
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)