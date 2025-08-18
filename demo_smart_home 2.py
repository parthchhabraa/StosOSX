#!/usr/bin/env python3
"""
Smart Home Integration Demo for StosOS

Demonstrates the smart home module functionality including:
- Device discovery and control
- Google Assistant and Alexa integration
- Scene management
- Voice command handling
- Real-time status updates
"""

import sys
import os
import time
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.smart_home import SmartHomeModule
from services.google_assistant_service import GoogleAssistantService
from services.alexa_service import AlexaService
from models.smart_device import SmartDevice, DeviceType, Platform


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


def demo_service_authentication():
    """Demo service authentication"""
    print_header("Service Authentication Demo")
    
    print("🔵 Testing Google Assistant Service...")
    google_service = GoogleAssistantService()
    
    if google_service.authenticate():
        print("✅ Google Assistant authentication successful")
        devices = google_service.get_devices()
        print(f"📱 Discovered {len(devices)} Google devices")
        
        for device in devices[:2]:  # Show first 2 devices
            print_device_info(device)
    else:
        print("❌ Google Assistant authentication failed")
    
    print("\n🟠 Testing Alexa Service...")
    alexa_service = AlexaService()
    
    if alexa_service.authenticate():
        print("✅ Alexa authentication successful")
        devices = alexa_service.get_devices()
        print(f"📱 Discovered {len(devices)} Alexa devices")
        
        for device in devices[:2]:  # Show first 2 devices
            print_device_info(device)
    else:
        print("❌ Alexa authentication failed")
    
    return google_service, alexa_service


def demo_device_control(google_service, alexa_service):
    """Demo device control functionality"""
    print_header("Device Control Demo")
    
    # Test Google device control
    google_devices = google_service.get_devices()
    if google_devices:
        device = google_devices[0]
        print(f"🔵 Controlling Google device: {device.name}")
        
        print("   💡 Turning device on...")
        if google_service.control_device(device.id, "power_on"):
            print("   ✅ Power on successful")
            print_device_info(device)
        
        if device.has_capability("brightness"):
            print("   🔆 Setting brightness to 75%...")
            if google_service.control_device(device.id, "set_brightness", {"brightness": 75}):
                print("   ✅ Brightness control successful")
                print_device_info(device)
        
        time.sleep(1)
        
        print("   💡 Turning device off...")
        if google_service.control_device(device.id, "power_off"):
            print("   ✅ Power off successful")
            print_device_info(device)
    
    # Test Alexa device control
    alexa_devices = alexa_service.get_devices()
    if alexa_devices:
        device = alexa_devices[0]
        print(f"\n🟠 Controlling Alexa device: {device.name}")
        
        print("   🔊 Turning device on...")
        if alexa_service.control_device(device.id, "power_on"):
            print("   ✅ Power on successful")
            print_device_info(device)
        
        if device.has_capability("volume"):
            print("   🔊 Setting volume to 60%...")
            if alexa_service.control_device(device.id, "set_volume", {"volume": 60}):
                print("   ✅ Volume control successful")
                print_device_info(device)


def demo_smart_home_module():
    """Demo the complete smart home module"""
    print_header("Smart Home Module Demo")
    
    print("🏠 Initializing Smart Home Module...")
    module = SmartHomeModule()
    
    if module.initialize():
        print("✅ Smart Home module initialized successfully")
        
        # Wait for services to authenticate
        time.sleep(2)
        
        print(f"📱 Total devices discovered: {len(module.devices)}")
        print(f"🏠 Rooms found: {len(module.rooms)}")
        
        # Show devices by room
        for room_name, room_devices in module.rooms.items():
            print(f"\n🏠 {room_name} ({len(room_devices)} devices):")
            for device in room_devices:
                print(f"   • {device.name} ({device.device_type.value})")
        
        # Demo voice commands
        print("\n🎤 Testing voice commands...")
        
        voice_commands = [
            "turn on the lights",
            "turn off all lights", 
            "activate study mode",
            "set bedroom temperature to 72"
        ]
        
        for command in voice_commands:
            print(f"   🎤 '{command}'")
            result = module.handle_voice_command(command)
            print(f"   {'✅' if result else '❌'} {'Handled' if result else 'Not handled'}")
        
        # Demo scene activation
        print("\n🎬 Testing scene activation...")
        for scene_name, scene_data in module.scenes.items():
            print(f"   🎬 Activating '{scene_name}'...")
            module._activate_scene(scene_name, scene_data)
            print(f"   ✅ Scene activated")
        
        # Demo room control
        if module.rooms:
            room_name = list(module.rooms.keys())[0]
            print(f"\n🏠 Testing room control for '{room_name}'...")
            
            print("   💡 Turning all devices on...")
            module._control_room(room_name, "power_on")
            print("   ✅ Room control executed")
            
            time.sleep(1)
            
            print("   💡 Turning all devices off...")
            module._control_room(room_name, "power_off")
            print("   ✅ Room control executed")
        
        # Cleanup
        module.cleanup()
        print("\n🧹 Module cleanup completed")
        
    else:
        print("❌ Smart Home module initialization failed")


def demo_scene_management():
    """Demo scene management functionality"""
    print_header("Scene Management Demo")
    
    # Create sample scene
    sample_scene = {
        "description": "Perfect lighting and temperature for studying",
        "devices": {
            "light_1": {
                "power": True,
                "brightness": 80,
                "color": "warm_white"
            },
            "thermostat_1": {
                "target_temperature": 72
            },
            "speaker_1": {
                "power": False
            }
        }
    }
    
    print("🎬 Sample Scene: 'Study Mode'")
    print(f"   Description: {sample_scene['description']}")
    print(f"   Devices configured: {len(sample_scene['devices'])}")
    
    for device_id, settings in sample_scene['devices'].items():
        print(f"   📱 {device_id}:")
        for setting, value in settings.items():
            print(f"      • {setting}: {value}")
    
    print("\n🎬 Scene activation would:")
    print("   1. Turn on living room lights at 80% brightness")
    print("   2. Set thermostat to 72°F")
    print("   3. Turn off background music")
    print("   4. Provide optimal study environment")


def demo_real_time_updates():
    """Demo real-time status updates"""
    print_header("Real-time Status Updates Demo")
    
    print("📡 Setting up device status monitoring...")
    
    # Create a callback to handle device updates
    update_count = 0
    
    def device_update_callback(device):
        nonlocal update_count
        update_count += 1
        print(f"   📡 Update #{update_count}: {device.name}")
        print(f"      Status: {device.status}")
        print(f"      Updated: {device.last_updated.strftime('%H:%M:%S')}")
    
    # Initialize services with callback
    google_service = GoogleAssistantService()
    alexa_service = AlexaService()
    
    if google_service.authenticate():
        google_service.add_device_callback(device_update_callback)
        print("✅ Google Assistant monitoring enabled")
    
    if alexa_service.authenticate():
        alexa_service.add_device_callback(device_update_callback)
        print("✅ Alexa monitoring enabled")
    
    # Simulate device changes
    print("\n🔄 Simulating device status changes...")
    
    google_devices = google_service.get_devices()
    if google_devices:
        device = google_devices[0]
        
        print(f"   🔄 Changing {device.name} status...")
        google_service.control_device(device.id, "power_on")
        
        if device.has_capability("brightness"):
            google_service.control_device(device.id, "set_brightness", {"brightness": 50})
        
        time.sleep(0.5)
        google_service.control_device(device.id, "power_off")
    
    print(f"\n📊 Total status updates received: {update_count}")


def main():
    """Main demo function"""
    print("🏠 StosOS Smart Home Integration Demo")
    print("=====================================")
    print("This demo showcases the smart home module capabilities")
    print("including device discovery, control, and scene management.")
    
    try:
        # Demo 1: Service Authentication
        google_service, alexa_service = demo_service_authentication()
        
        # Demo 2: Device Control
        demo_device_control(google_service, alexa_service)
        
        # Demo 3: Complete Module
        demo_smart_home_module()
        
        # Demo 4: Scene Management
        demo_scene_management()
        
        # Demo 5: Real-time Updates
        demo_real_time_updates()
        
        print_header("Demo Complete")
        print("✅ All smart home functionality demonstrated successfully!")
        print("\n🎯 Key Features Demonstrated:")
        print("   • Google Assistant SDK integration")
        print("   • Alexa Voice Service integration")
        print("   • Device discovery and control")
        print("   • Room-based device grouping")
        print("   • Scene management and activation")
        print("   • Voice command handling")
        print("   • Real-time status monitoring")
        print("   • Cross-platform device control")
        
        print("\n📝 Next Steps:")
        print("   • Configure actual Google/Alexa credentials")
        print("   • Set up real smart home devices")
        print("   • Create custom scenes for your needs")
        print("   • Integrate with voice assistant module")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()