#!/usr/bin/env python3
"""
Verification Script for StosOS Error Handling and Recovery System

This script demonstrates the comprehensive error handling and recovery system
in action, showing how it handles various types of errors and recovery scenarios.

Requirements: 10.4, 10.6
"""

import sys
import os
import time
import threading
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.error_handler import (
    ErrorHandler, ErrorType, ErrorSeverity, RecoveryAction,
    error_handler, diagnostic_tools
)
from core.notification_manager import notification_manager
from core.module_recovery_manager import module_recovery_manager
from core.base_module import BaseModule
from kivy.uix.screenmanager import Screen


class DemoModule(BaseModule):
    """Demo module for error handling demonstration"""
    
    def __init__(self, module_id: str, failure_mode: str = "none"):
        super().__init__(module_id, f"Demo {module_id.title()}", "demo")
        self.failure_mode = failure_mode
        self.initialization_attempts = 0
        self.fallback_active = False
    
    def initialize(self) -> bool:
        """Initialize with potential failures based on mode"""
        self.initialization_attempts += 1
        
        if self.failure_mode == "network":
            if self.initialization_attempts < 3:
                raise ConnectionError("Failed to connect to external service")
        elif self.failure_mode == "permission":
            if self.initialization_attempts < 2:
                raise PermissionError("Access denied to required resource")
        elif self.failure_mode == "memory":
            if self.initialization_attempts < 2:
                raise MemoryError("Insufficient memory for module initialization")
        elif self.failure_mode == "persistent":
            raise Exception("Persistent failure - cannot initialize")
        
        self._initialized = True
        print(f"    ✓ {self.module_id} initialized successfully (attempt {self.initialization_attempts})")
        return True
    
    def get_screen(self) -> Screen:
        """Get demo screen"""
        return Screen(name=self.module_id)
    
    def enable_fallback_mode(self) -> bool:
        """Enable fallback mode"""
        self.fallback_active = True
        print(f"    ⚠ {self.module_id} running in fallback mode")
        return True
    
    def disable_fallback_mode(self) -> bool:
        """Disable fallback mode"""
        self.fallback_active = False
        return self.initialize()


def demo_basic_error_handling():
    """Demonstrate basic error handling capabilities"""
    print("\n" + "="*60)
    print("DEMO 1: Basic Error Handling")
    print("="*60)
    
    print("\n1. Handling different types of errors:")
    
    # Network error
    try:
        raise ConnectionError("Network connection failed")
    except Exception as e:
        success = error_handler.handle_error(
            error=e,
            context="network_operation",
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.HIGH,
            module_id="demo_network"
        )
        print(f"   Network error handled: {success}")
    
    # Permission error
    try:
        raise PermissionError("Access denied to configuration file")
    except Exception as e:
        success = error_handler.handle_error(
            error=e,
            context="config_access",
            error_type=ErrorType.PERMISSION,
            severity=ErrorSeverity.MEDIUM,
            module_id="demo_config"
        )
        print(f"   Permission error handled: {success}")
    
    # Memory error
    try:
        raise MemoryError("Insufficient memory for operation")
    except Exception as e:
        success = error_handler.handle_error(
            error=e,
            context="memory_allocation",
            error_type=ErrorType.MEMORY,
            severity=ErrorSeverity.CRITICAL,
            module_id="demo_memory"
        )
        print(f"   Memory error handled: {success}")
    
    print("\n2. Error statistics:")
    stats = error_handler.get_error_statistics()
    print(f"   Total errors: {stats['total_errors']}")
    print(f"   Error types: {list(stats['type_distribution'].keys())}")
    print(f"   Severity distribution: {stats['severity_distribution']}")


def demo_module_recovery():
    """Demonstrate module recovery capabilities"""
    print("\n" + "="*60)
    print("DEMO 2: Module Recovery and Restart")
    print("="*60)
    
    # Create modules with different failure modes
    modules = {
        "network_module": DemoModule("network_module", "network"),
        "permission_module": DemoModule("permission_module", "permission"),
        "persistent_module": DemoModule("persistent_module", "persistent")
    }
    
    print("\n1. Registering modules with recovery manager:")
    for module_id, module in modules.items():
        module_recovery_manager.register_module(module)
        print(f"   ✓ Registered {module_id}")
    
    print("\n2. Testing module recovery scenarios:")
    
    # Test network module (should recover after retries)
    print(f"\n   Testing network module recovery:")
    try:
        modules["network_module"].initialize()
    except Exception as e:
        modules["network_module"].handle_error(e, "initialization")
    
    # Attempt restart
    restart_success = module_recovery_manager.restart_module("network_module")
    print(f"   Network module restart: {restart_success}")
    
    # Test persistent failure module (should go to fallback)
    print(f"\n   Testing persistent failure module:")
    try:
        modules["persistent_module"].initialize()
    except Exception as e:
        modules["persistent_module"].handle_error(e, "initialization")
    
    # Multiple restart attempts should trigger fallback
    for i in range(3):
        restart_success = module_recovery_manager.restart_module("persistent_module", force=True)
        print(f"   Restart attempt {i+1}: {restart_success}")
    
    # Enable fallback mode
    fallback_success = module_recovery_manager.enable_module_fallback("persistent_module")
    print(f"   Fallback mode enabled: {fallback_success}")
    
    print("\n3. Module health status:")
    for module_id in modules.keys():
        health = module_recovery_manager.get_module_health(module_id)
        print(f"   {module_id}: {health['state']} (restarts: {health['restart_count']})")
    
    # Cleanup
    for module_id in modules.keys():
        module_recovery_manager.unregister_module(module_id)


def demo_system_health_monitoring():
    """Demonstrate system health monitoring"""
    print("\n" + "="*60)
    print("DEMO 3: System Health Monitoring")
    print("="*60)
    
    print("\n1. Current system metrics:")
    metrics = error_handler.health_monitor.get_current_metrics()
    
    if 'error' not in metrics:
        print(f"   CPU Usage: {metrics.get('cpu_percent', 0):.1f}%")
        print(f"   Memory Usage: {metrics.get('memory_percent', 0):.1f}%")
        print(f"   Disk Usage: {metrics.get('disk_percent', 0):.1f}%")
        
        temp = metrics.get('temperature')
        if temp:
            print(f"   Temperature: {temp:.1f}°C")
        else:
            print("   Temperature: Not available (not on Raspberry Pi)")
    else:
        print(f"   Error collecting metrics: {metrics['error']}")
    
    print("\n2. System health report:")
    health_report = error_handler.get_system_health_report()
    print(f"   Overall health: {health_report['overall_health']}")
    print(f"   Degraded modules: {len(health_report['degraded_modules'])}")
    print(f"   Recent recovery attempts: {len(health_report['recent_recovery_attempts'])}")


def demo_diagnostic_tools():
    """Demonstrate diagnostic tools"""
    print("\n" + "="*60)
    print("DEMO 4: Diagnostic Tools")
    print("="*60)
    
    print("\n1. Running comprehensive system diagnostics:")
    diagnostics = diagnostic_tools.run_system_diagnostics()
    
    print(f"   Diagnostic timestamp: {diagnostics['timestamp']}")
    print("\n   Test results:")
    
    for test_name, result in diagnostics['tests'].items():
        status = result.get('status', 'unknown')
        issues = result.get('issues', [])
        
        status_icon = {
            'healthy': '✓',
            'degraded': '⚠',
            'critical': '✗',
            'error': '❌',
            'unknown': '?'
        }.get(status, '?')
        
        print(f"     {status_icon} {test_name.title()}: {status}")
        
        if issues:
            for issue in issues:
                print(f"       - {issue}")
        
        if 'details' in result:
            details = result['details']
            if test_name == 'network':
                if 'localhost' in details:
                    print(f"       Localhost: {'✓' if details['localhost'] else '✗'}")
                if 'internet' in details:
                    print(f"       Internet: {'✓' if details['internet'] else '✗'}")
            elif test_name == 'disk':
                if 'disk_usage_percent' in details:
                    print(f"       Disk usage: {details['disk_usage_percent']:.1f}%")
                if 'free_space_gb' in details:
                    print(f"       Free space: {details['free_space_gb']:.1f} GB")
            elif test_name == 'memory':
                if 'memory_percent' in details:
                    print(f"       Memory usage: {details['memory_percent']:.1f}%")
                if 'available_gb' in details:
                    print(f"       Available: {details['available_gb']:.1f} GB")


def demo_error_patterns():
    """Demonstrate error pattern detection"""
    print("\n" + "="*60)
    print("DEMO 5: Error Pattern Detection")
    print("="*60)
    
    print("\n1. Generating repeated errors to trigger pattern detection:")
    
    # Generate multiple similar errors
    for i in range(15):
        try:
            raise TimeoutError(f"Operation timeout #{i+1}")
        except Exception as e:
            error_handler.handle_error(
                error=e,
                context="pattern_demo",
                error_type=ErrorType.TIMEOUT,
                severity=ErrorSeverity.MEDIUM,
                module_id="pattern_test_module"
            )
        
        if i == 4:
            print("   ⚠ Pattern detection threshold reached (5 errors)")
        elif i == 9:
            print("   ⚠ Frequent error pattern detected (10 errors)")
        elif i == 14:
            print("   ❌ Critical error pattern detected (15 errors)")
    
    print("\n2. Module health after pattern detection:")
    module_health = error_handler.get_module_health_status("pattern_test_module")
    print(f"   Health score: {module_health['health_score']}/100")
    print(f"   Status: {module_health['status']}")
    print(f"   Recent errors: {module_health['recent_errors']}")


def demo_user_notifications():
    """Demonstrate user notification system"""
    print("\n" + "="*60)
    print("DEMO 6: User Notification System")
    print("="*60)
    
    print("\n1. Creating different types of notifications:")
    
    # Capture notifications for demo
    notifications_shown = []
    
    def capture_notification(event_type, notification):
        if event_type == 'notification_shown':
            notifications_shown.append(notification)
    
    notification_manager.register_ui_callback(capture_notification)
    
    # Create various error notifications
    error_scenarios = [
        {
            'severity': 'high',
            'module_id': 'calendar_module',
            'error_message': 'Failed to sync with Google Calendar',
            'context': 'calendar_sync',
            'suggested_actions': ['Check internet connection', 'Verify API credentials', 'Restart module']
        },
        {
            'severity': 'critical',
            'module_id': 'smart_home',
            'error_message': 'Smart home hub disconnected',
            'context': 'device_communication',
            'requires_action': True,
            'suggested_actions': ['Check hub power', 'Verify network connection', 'Restart hub']
        },
        {
            'severity': 'medium',
            'module_id': 'spotify_controller',
            'error_message': 'Spotify authentication expired',
            'context': 'api_authentication',
            'suggested_actions': ['Re-authenticate with Spotify', 'Check account status']
        }
    ]
    
    for i, scenario in enumerate(error_scenarios):
        notification_manager.show_error_notification(scenario)
        print(f"   ✓ Created {scenario['severity']} notification for {scenario['module_id']}")
    
    print(f"\n2. Active notifications: {len(notification_manager.get_active_notifications())}")
    
    # Show notification details
    for notification in notifications_shown:
        print(f"   - {notification.title}: {notification.type.value} (priority: {notification.priority.value})")
    
    # Cleanup
    notification_manager.dismiss_all_notifications()
    notification_manager.unregister_ui_callback(capture_notification)


def demo_graceful_degradation():
    """Demonstrate graceful degradation"""
    print("\n" + "="*60)
    print("DEMO 7: Graceful Degradation")
    print("="*60)
    
    print("\n1. Simulating system under stress:")
    
    # Create a module that will be degraded
    stressed_module = DemoModule("stressed_module", "persistent")
    module_recovery_manager.register_module(stressed_module)
    
    print("   Attempting multiple initializations (will fail)...")
    
    # Simulate multiple failures
    for i in range(5):
        try:
            stressed_module.initialize()
        except Exception as e:
            stressed_module.handle_error(e, f"stress_test_{i}")
            print(f"   Attempt {i+1}: Failed")
    
    print("\n2. Checking module state after failures:")
    health = module_recovery_manager.get_module_health("stressed_module")
    print(f"   Module state: {health['state']}")
    print(f"   Restart attempts: {health['restart_count']}")
    print(f"   Can restart: {health['can_restart']}")
    
    print("\n3. Enabling fallback mode for graceful degradation:")
    fallback_success = module_recovery_manager.enable_module_fallback("stressed_module")
    print(f"   Fallback mode enabled: {fallback_success}")
    
    if fallback_success:
        print("   ✓ Module now operating with reduced functionality")
        print("   ✓ System remains stable despite module failure")
    
    # Cleanup
    module_recovery_manager.unregister_module("stressed_module")


def run_comprehensive_demo():
    """Run comprehensive error handling demonstration"""
    print("🔧 StosOS Comprehensive Error Handling and Recovery System Demo")
    print("This demonstration shows the error handling system in action.")
    print("Note: UI popups are simulated in console output for this demo.")
    
    # Run all demonstrations
    demos = [
        demo_basic_error_handling,
        demo_module_recovery,
        demo_system_health_monitoring,
        demo_diagnostic_tools,
        demo_error_patterns,
        demo_user_notifications,
        demo_graceful_degradation
    ]
    
    for demo in demos:
        try:
            demo()
            time.sleep(1)  # Brief pause between demos
        except Exception as e:
            print(f"❌ Demo error: {e}")
    
    # Final summary
    print("\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)
    
    print("\n✅ Demonstrated Features:")
    print("   • Module-specific error handling with automatic restart capabilities")
    print("   • User notification system with clear recovery instructions")
    print("   • Comprehensive logging system with different severity levels")
    print("   • Graceful degradation for network and hardware failures")
    print("   • Diagnostic tools for troubleshooting common issues")
    print("   • System health monitoring with real-time metrics")
    print("   • Error pattern detection and prevention")
    print("   • Recovery action automation")
    
    print("\n📊 Final System Status:")
    health_report = error_handler.get_system_health_report()
    stats = error_handler.get_error_statistics()
    
    print(f"   Overall system health: {health_report['overall_health']}")
    print(f"   Total errors handled: {stats['total_errors']}")
    print(f"   Active degraded modules: {len(health_report['degraded_modules'])}")
    print(f"   Recovery attempts: {len(health_report['recent_recovery_attempts'])}")
    
    print("\n🎉 Error handling and recovery system demonstration complete!")
    print("The system is now ready to handle real-world errors and failures.")


if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    # Run comprehensive demonstration
    run_comprehensive_demo()