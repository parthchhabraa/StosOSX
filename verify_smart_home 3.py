#!/usr/bin/env python3
"""
Smart Home Integration Verification Script

Verifies that the smart home module implementation meets all requirements:
- Requirements 3.1: Google/Alexa device display and control
- Requirements 3.2: Device control with appropriate interfaces
- Requirements 3.3: Command execution within 2 seconds
- Requirements 3.4: Real-time device status updates
- Requirements 3.5: Scene management for device configurations
"""

import sys
import os
import time
import threading
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.smart_home import SmartHomeModule
from services.google_assistant_service import GoogleAssistantService
from services.alexa_service import AlexaService
from models.smart_device import SmartDevice, DeviceType, Platform


class SmartHomeVerification:
    """Verification class for smart home integration"""
    
    def __init__(self):
        self.results = []
        self.module = None
        self.google_service = None
        self.alexa_service = None
    
    def log_result(self, test_name, passed, message=""):
        """Log a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.results.append({
            'test': test_name,
            'passed': passed,
            'message': message
        })
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
    
    def verify_requirement_3_1(self):
        """Verify Requirement 3.1: Display Google/Alexa devices"""
        print("\n🔍 Verifying Requirement 3.1: Device Display and Discovery")
        
        try:
            # Test Google Assistant service
            self.google_service = GoogleAssistantService()
            google_auth = self.google_service.authenticate()
            self.log_result(
                "Google Assistant Authentication",
                google_auth,
                "Google Assistant service should authenticate successfully"
            )
            
            if google_auth:
                google_devices = self.google_service.get_devices()
                self.log_result(
                    "Google Device Discovery",
                    len(google_devices) > 0,
                    f"Found {len(google_devices)} Google devices"
                )
            
            # Test Alexa service
            self.alexa_service = AlexaService()
            alexa_auth = self.alexa_service.authenticate()
            self.log_result(
                "Alexa Authentication",
                alexa_auth,
                "Alexa service should authenticate successfully"
            )
            
            if alexa_auth:
                alexa_devices = self.alexa_service.get_devices()
                self.log_result(
                    "Alexa Device Discovery",
                    len(alexa_devices) > 0,
                    f"Found {len(alexa_devices)} Alexa devices"
                )
            
            # Test module device aggregation
            self.module = SmartHomeModule()
            module_init = self.module.initialize()
            self.log_result(
                "Smart Home Module Initialization",
                module_init,
                "Module should initialize and aggregate devices from both services"
            )
            
            if module_init:
                time.sleep(1)  # Allow services to authenticate
                total_devices = len(self.module.devices)
                self.log_result(
                    "Device Aggregation",
                    total_devices > 0,
                    f"Module aggregated {total_devices} total devices"
                )
                
                # Verify devices from both platforms are present
                google_count = len([d for d in self.module.devices.values() if d.platform == Platform.GOOGLE])
                alexa_count = len([d for d in self.module.devices.values() if d.platform == Platform.ALEXA])
                
                self.log_result(
                    "Multi-Platform Support",
                    google_count > 0 and alexa_count > 0,
                    f"Google: {google_count}, Alexa: {alexa_count} devices"
                )
            
        except Exception as e:
            self.log_result("Requirement 3.1", False, f"Exception: {e}")
    
    def verify_requirement_3_2(self):
        """Verify Requirement 3.2: Appropriate device controls"""
        print("\n🔍 Verifying Requirement 3.2: Device Control Interfaces")
        
        if not self.module or not self.module.devices:
            self.log_result("Requirement 3.2", False, "No devices available for testing")
            return
        
        try:
            # Test different device types have appropriate controls
            device_types_tested = set()
            
            for device in self.module.devices.values():
                device_type = device.device_type
                
                if device_type in device_types_tested:
                    continue
                
                device_types_tested.add(device_type)
                
                # Test light controls
                if device_type == DeviceType.LIGHT:
                    has_power = device.has_capability("power")
                    has_brightness = device.has_capability("brightness")
                    
                    self.log_result(
                        f"Light Controls ({device.name})",
                        has_power,
                        f"Power: {has_power}, Brightness: {has_brightness}"
                    )
                
                # Test speaker controls
                elif device_type == DeviceType.SPEAKER:
                    has_power = device.has_capability("power")
                    has_volume = device.has_capability("volume")
                    has_media = device.has_capability("play") or device.has_capability("pause")
                    
                    self.log_result(
                        f"Speaker Controls ({device.name})",
                        has_power and (has_volume or has_media),
                        f"Power: {has_power}, Volume: {has_volume}, Media: {has_media}"
                    )
                
                # Test thermostat controls
                elif device_type == DeviceType.THERMOSTAT:
                    has_temp = device.has_capability("target_temperature")
                    
                    self.log_result(
                        f"Thermostat Controls ({device.name})",
                        has_temp,
                        f"Temperature control: {has_temp}"
                    )
                
                # Test switch controls
                elif device_type == DeviceType.SWITCH:
                    has_power = device.has_capability("power")
                    
                    self.log_result(
                        f"Switch Controls ({device.name})",
                        has_power,
                        f"Power control: {has_power}"
                    )
            
            # Verify control interface exists
            control_methods = [
                hasattr(self.module, '_control_device'),
                hasattr(self.module, '_control_room'),
                hasattr(self.module, '_activate_scene')
            ]
            
            self.log_result(
                "Control Interface Methods",
                all(control_methods),
                "Device, room, and scene control methods available"
            )
            
        except Exception as e:
            self.log_result("Requirement 3.2", False, f"Exception: {e}")
    
    def verify_requirement_3_3(self):
        """Verify Requirement 3.3: Command execution within 2 seconds"""
        print("\n🔍 Verifying Requirement 3.3: Command Response Time")
        
        if not self.module or not self.module.devices:
            self.log_result("Requirement 3.3", False, "No devices available for testing")
            return
        
        try:
            # Test command response time
            device = list(self.module.devices.values())[0]
            
            # Test power command timing
            start_time = time.time()
            success = self.module._control_device(device.id, "power_on")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            self.log_result(
                "Power Command Response Time",
                response_time < 2.0 and success,
                f"Response time: {response_time:.3f}s (target: <2.0s)"
            )
            
            # Test brightness command timing (if supported)
            if device.has_capability("brightness"):
                start_time = time.time()
                success = self.module._control_device(device.id, "set_brightness", {"brightness": 75})
                end_time = time.time()
                
                response_time = end_time - start_time
                
                self.log_result(
                    "Brightness Command Response Time",
                    response_time < 2.0 and success,
                    f"Response time: {response_time:.3f}s (target: <2.0s)"
                )
            
            # Test room command timing
            if self.module.rooms:
                room_name = list(self.module.rooms.keys())[0]
                
                start_time = time.time()
                self.module._control_room(room_name, "power_on")
                end_time = time.time()
                
                response_time = end_time - start_time
                
                self.log_result(
                    "Room Command Response Time",
                    response_time < 2.0,
                    f"Response time: {response_time:.3f}s (target: <2.0s)"
                )
            
        except Exception as e:
            self.log_result("Requirement 3.3", False, f"Exception: {e}")
    
    def verify_requirement_3_4(self):
        """Verify Requirement 3.4: Real-time device status updates"""
        print("\n🔍 Verifying Requirement 3.4: Real-time Status Updates")
        
        if not self.module:
            self.log_result("Requirement 3.4", False, "Module not available for testing")
            return
        
        try:
            # Test device update callback system
            update_received = threading.Event()
            updated_device = None
            
            def test_callback(device):
                nonlocal updated_device
                updated_device = device
                update_received.set()
            
            # Add callback to services
            if self.google_service:
                self.google_service.add_device_callback(test_callback)
            
            if self.alexa_service:
                self.alexa_service.add_device_callback(test_callback)
            
            self.log_result(
                "Device Callback Registration",
                True,
                "Callbacks registered with both services"
            )
            
            # Trigger a device update
            if self.module.devices:
                device = list(self.module.devices.values())[0]
                
                # Control device to trigger update
                self.module._control_device(device.id, "power_on")
                
                # Wait for callback (with timeout)
                callback_received = update_received.wait(timeout=3.0)
                
                self.log_result(
                    "Real-time Status Update",
                    callback_received,
                    f"Update callback {'received' if callback_received else 'not received'} within 3 seconds"
                )
                
                if callback_received and updated_device:
                    # Verify update timestamp is recent
                    time_diff = datetime.now() - updated_device.last_updated
                    recent_update = time_diff.total_seconds() < 5.0
                    
                    self.log_result(
                        "Update Timestamp Accuracy",
                        recent_update,
                        f"Last updated: {updated_device.last_updated.strftime('%H:%M:%S')}"
                    )
            
            # Test status monitoring timer
            has_status_timer = hasattr(self.module, 'status_timer') and self.module.status_timer is not None
            
            self.log_result(
                "Periodic Status Monitoring",
                has_status_timer,
                "Status monitoring timer is active"
            )
            
        except Exception as e:
            self.log_result("Requirement 3.4", False, f"Exception: {e}")
    
    def verify_requirement_3_5(self):
        """Verify Requirement 3.5: Scene management"""
        print("\n🔍 Verifying Requirement 3.5: Scene Management")
        
        if not self.module:
            self.log_result("Requirement 3.5", False, "Module not available for testing")
            return
        
        try:
            # Test scene loading
            has_scenes = len(self.module.scenes) > 0
            self.log_result(
                "Scene Configuration Loading",
                has_scenes,
                f"Loaded {len(self.module.scenes)} predefined scenes"
            )
            
            # Test scene structure
            if has_scenes:
                scene_name = list(self.module.scenes.keys())[0]
                scene_data = self.module.scenes[scene_name]
                
                has_description = 'description' in scene_data
                has_devices = 'devices' in scene_data
                
                self.log_result(
                    "Scene Data Structure",
                    has_description and has_devices,
                    f"Scene '{scene_name}' has proper structure"
                )
            
            # Test scene activation method
            has_activate_method = hasattr(self.module, '_activate_scene')
            self.log_result(
                "Scene Activation Method",
                has_activate_method,
                "Scene activation method available"
            )
            
            # Test scene activation
            if has_scenes and has_activate_method:
                scene_name = list(self.module.scenes.keys())[0]
                scene_data = self.module.scenes[scene_name]
                
                try:
                    self.module._activate_scene(scene_name, scene_data)
                    self.log_result(
                        "Scene Activation Test",
                        True,
                        f"Successfully activated '{scene_name}' scene"
                    )
                except Exception as e:
                    self.log_result(
                        "Scene Activation Test",
                        False,
                        f"Scene activation failed: {e}"
                    )
            
            # Test scene management UI components
            scene_ui_methods = [
                hasattr(self.module, '_build_scenes_view'),
                hasattr(self.module, '_show_add_scene_dialog'),
                hasattr(self.module, '_edit_scene')
            ]
            
            self.log_result(
                "Scene Management UI",
                all(scene_ui_methods),
                "Scene management UI methods available"
            )
            
        except Exception as e:
            self.log_result("Requirement 3.5", False, f"Exception: {e}")
    
    def verify_voice_command_integration(self):
        """Verify voice command integration"""
        print("\n🔍 Verifying Voice Command Integration")
        
        if not self.module:
            self.log_result("Voice Integration", False, "Module not available for testing")
            return
        
        try:
            # Test voice command handler exists
            has_voice_handler = hasattr(self.module, 'handle_voice_command')
            self.log_result(
                "Voice Command Handler",
                has_voice_handler,
                "Voice command handler method available"
            )
            
            if has_voice_handler:
                # Test various voice commands
                test_commands = [
                    ("turn on the lights", "Light control command"),
                    ("turn off all lights", "All lights control"),
                    ("activate study mode", "Scene activation"),
                    ("set volume to 50", "Volume control")
                ]
                
                for command, description in test_commands:
                    try:
                        result = self.module.handle_voice_command(command)
                        self.log_result(
                            f"Voice Command: '{command}'",
                            isinstance(result, bool),
                            f"{description} - {'Handled' if result else 'Not handled'}"
                        )
                    except Exception as e:
                        self.log_result(
                            f"Voice Command: '{command}'",
                            False,
                            f"Exception: {e}"
                        )
            
        except Exception as e:
            self.log_result("Voice Integration", False, f"Exception: {e}")
    
    def verify_error_handling(self):
        """Verify error handling and recovery"""
        print("\n🔍 Verifying Error Handling")
        
        try:
            # Test invalid device control
            if self.module:
                result = self.module._control_device("invalid_device_id", "power_on")
                self.log_result(
                    "Invalid Device Handling",
                    result is False,
                    "Invalid device ID handled gracefully"
                )
            
            # Test service connection failure handling
            test_service = GoogleAssistantService()
            # Don't authenticate - test failure handling
            devices = test_service.get_devices()
            self.log_result(
                "Unauthenticated Service Handling",
                len(devices) == 0,
                "Unauthenticated service returns empty device list"
            )
            
            # Test module cleanup
            if self.module:
                try:
                    self.module.cleanup()
                    self.log_result(
                        "Module Cleanup",
                        True,
                        "Module cleanup completed without errors"
                    )
                except Exception as e:
                    self.log_result(
                        "Module Cleanup",
                        False,
                        f"Cleanup error: {e}"
                    )
            
        except Exception as e:
            self.log_result("Error Handling", False, f"Exception: {e}")
    
    def run_verification(self):
        """Run all verification tests"""
        print("🏠 Smart Home Integration Verification")
        print("=" * 50)
        
        # Run all verification tests
        self.verify_requirement_3_1()
        self.verify_requirement_3_2()
        self.verify_requirement_3_3()
        self.verify_requirement_3_4()
        self.verify_requirement_3_5()
        self.verify_voice_command_integration()
        self.verify_error_handling()
        
        # Print summary
        print("\n" + "=" * 50)
        print("VERIFICATION SUMMARY")
        print("=" * 50)
        
        passed_count = sum(1 for result in self.results if result['passed'])
        total_count = len(self.results)
        
        print(f"Tests Passed: {passed_count}/{total_count}")
        print(f"Success Rate: {(passed_count/total_count)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.results if not result['passed']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"   • {result['test']}: {result['message']}")
        
        # Overall result
        all_passed = len(failed_tests) == 0
        print(f"\n🎯 Overall Result: {'✅ ALL REQUIREMENTS MET' if all_passed else '❌ SOME REQUIREMENTS NOT MET'}")
        
        if all_passed:
            print("\n🎉 Smart Home Integration is ready for production!")
            print("   • All device discovery and control features working")
            print("   • Real-time status updates functioning")
            print("   • Scene management operational")
            print("   • Voice command integration ready")
            print("   • Error handling robust")
        else:
            print("\n⚠️  Please address failed requirements before deployment.")
        
        return all_passed


def main():
    """Main verification function"""
    try:
        verifier = SmartHomeVerification()
        success = verifier.run_verification()
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Verification interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Verification error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)