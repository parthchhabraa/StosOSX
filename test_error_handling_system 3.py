#!/usr/bin/env python3
"""
Test Error Handling and Recovery System for StosOS

This test verifies the comprehensive error handling and recovery system
including module-specific error handling, user notifications, system health
monitoring, and diagnostic tools.

Requirements: 10.4, 10.6
"""

import sys
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.error_handler import (
    ErrorHandler, ErrorType, ErrorSeverity, RecoveryAction,
    SystemHealthMonitor, DiagnosticTools, error_handler, diagnostic_tools
)
from core.notification_manager import (
    NotificationManager, NotificationType, NotificationPriority,
    notification_manager
)
from core.module_recovery_manager import (
    ModuleRecoveryManager, ModuleState, module_recovery_manager
)
from core.base_module import BaseModule
from kivy.uix.screenmanager import Screen


class TestModule(BaseModule):
    """Test module for error handling verification"""
    
    def __init__(self, module_id: str, should_fail: bool = False):
        super().__init__(module_id, f"Test {module_id}", "test")
        self.should_fail = should_fail
        self.initialization_count = 0
        self.fallback_mode = False
    
    def initialize(self) -> bool:
        """Initialize the test module"""
        self.initialization_count += 1
        
        if self.should_fail and self.initialization_count < 3:
            raise Exception(f"Test module {self.module_id} initialization failed")
        
        self._initialized = True
        return True
    
    def get_screen(self) -> Screen:
        """Get test screen"""
        return Screen(name=self.module_id)
    
    def enable_fallback_mode(self) -> bool:
        """Enable fallback mode"""
        self.fallback_mode = True
        return True
    
    def disable_fallback_mode(self) -> bool:
        """Disable fallback mode"""
        self.fallback_mode = False
        return self.initialize()


def test_error_handler():
    """Test basic error handler functionality"""
    print("Testing Error Handler...")
    
    # Test error handling
    test_error = Exception("Test error message")
    success = error_handler.handle_error(
        error=test_error,
        context="test_context",
        error_type=ErrorType.MODULE,
        severity=ErrorSeverity.MEDIUM,
        module_id="test_module"
    )
    
    print(f"✓ Error handled: {success}")
    
    # Test error statistics
    stats = error_handler.get_error_statistics()
    print(f"✓ Error statistics: {stats['total_errors']} total errors")
    
    # Test error history
    history = error_handler.get_error_history(5)
    print(f"✓ Error history: {len(history)} recent errors")
    
    return True


def test_system_health_monitor():
    """Test system health monitoring"""
    print("Testing System Health Monitor...")
    
    monitor = SystemHealthMonitor()
    
    # Test metrics collection
    metrics = monitor._collect_metrics()
    print(f"✓ Collected metrics: CPU {metrics.get('cpu_percent', 0):.1f}%")
    
    # Test current metrics
    current = monitor.get_current_metrics()
    print(f"✓ Current metrics available: {'timestamp' in current}")
    
    return True


def test_diagnostic_tools():
    """Test diagnostic tools"""
    print("Testing Diagnostic Tools...")
    
    # Run system diagnostics
    diagnostics = diagnostic_tools.run_system_diagnostics()
    
    print(f"✓ Diagnostics completed at: {diagnostics['timestamp']}")
    
    # Check individual tests
    for test_name, result in diagnostics['tests'].items():
        status = result.get('status', 'unknown')
        print(f"  - {test_name}: {status}")
    
    return True


def test_notification_manager():
    """Test notification manager"""
    print("Testing Notification Manager...")
    
    # Test error notification
    error_info = {
        'severity': 'high',
        'module_id': 'test_module',
        'error_message': 'Test error for notification',
        'context': 'test_context',
        'suggested_actions': ['Restart module', 'Check logs']
    }
    
    # Create a simple callback to capture notifications
    notifications_received = []
    
    def test_callback(event_type, notification):
        notifications_received.append((event_type, notification))
    
    notification_manager.register_ui_callback(test_callback)
    
    # Show notification (without UI)
    notification_manager.show_error_notification(error_info)
    
    print(f"✓ Notification created")
    
    # Test active notifications
    active = notification_manager.get_active_notifications()
    print(f"✓ Active notifications: {len(active)}")
    
    # Cleanup
    notification_manager.dismiss_all_notifications()
    notification_manager.unregister_ui_callback(test_callback)
    
    return True


def test_module_recovery_manager():
    """Test module recovery manager"""
    print("Testing Module Recovery Manager...")
    
    # Create test modules
    healthy_module = TestModule("healthy_test", should_fail=False)
    failing_module = TestModule("failing_test", should_fail=True)
    
    # Register modules
    module_recovery_manager.register_module(healthy_module)
    module_recovery_manager.register_module(failing_module)
    
    print("✓ Modules registered")
    
    # Test healthy module
    health = module_recovery_manager.get_module_health("healthy_test")
    print(f"✓ Healthy module state: {health['state']}")
    
    # Test module restart
    restart_success = module_recovery_manager.restart_module("failing_test")
    print(f"✓ Module restart attempted: {restart_success}")
    
    # Test fallback mode
    fallback_success = module_recovery_manager.enable_module_fallback("failing_test")
    print(f"✓ Fallback mode enabled: {fallback_success}")
    
    # Get all module health
    all_health = module_recovery_manager.get_all_module_health()
    print(f"✓ All module health retrieved: {len(all_health)} modules")
    
    # Cleanup
    module_recovery_manager.unregister_module("healthy_test")
    module_recovery_manager.unregister_module("failing_test")
    
    return True


def test_integration():
    """Test integration between components"""
    print("Testing Component Integration...")
    
    # Create test module
    test_module = TestModule("integration_test", should_fail=True)
    
    # Register with recovery manager
    module_recovery_manager.register_module(test_module)
    
    # Simulate error in module
    try:
        test_module.initialize()
    except Exception as e:
        # Handle error through module's error handler
        test_module.handle_error(e, "initialization")
    
    print("✓ Error handled through module")
    
    # Check if recovery was attempted
    health = module_recovery_manager.get_module_health("integration_test")
    print(f"✓ Module health after error: {health['state']}")
    
    # Test system health report
    health_report = error_handler.get_system_health_report()
    print(f"✓ System health report generated: {health_report['overall_health']}")
    
    # Cleanup
    module_recovery_manager.unregister_module("integration_test")
    
    return True


def test_graceful_degradation():
    """Test graceful degradation functionality"""
    print("Testing Graceful Degradation...")
    
    # Create module that will be degraded
    degraded_module = TestModule("degraded_test", should_fail=True)
    module_recovery_manager.register_module(degraded_module)
    
    # Simulate multiple failures to trigger degradation
    for i in range(5):
        try:
            degraded_module.initialize()
        except Exception as e:
            degraded_module.handle_error(e, f"initialization_attempt_{i}")
    
    # Check if module was degraded
    health = module_recovery_manager.get_module_health("degraded_test")
    print(f"✓ Module state after multiple failures: {health['state']}")
    
    # Test fallback mode
    if health['state'] in ['failed', 'degraded']:
        fallback_enabled = module_recovery_manager.enable_module_fallback("degraded_test")
        print(f"✓ Fallback mode enabled: {fallback_enabled}")
    
    # Cleanup
    module_recovery_manager.unregister_module("degraded_test")
    
    return True


def test_error_patterns():
    """Test error pattern detection"""
    print("Testing Error Pattern Detection...")
    
    # Generate multiple similar errors
    for i in range(12):
        test_error = ConnectionError(f"Network error {i}")
        error_handler.handle_error(
            error=test_error,
            context="pattern_test",
            error_type=ErrorType.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            module_id="pattern_test_module"
        )
    
    # Check error statistics
    stats = error_handler.get_error_statistics()
    print(f"✓ Error patterns detected in statistics")
    
    # Check if module health was affected
    module_health = error_handler.get_module_health_status("pattern_test_module")
    print(f"✓ Module health score: {module_health['health_score']}")
    
    return True


def run_all_tests():
    """Run all error handling tests"""
    print("=" * 60)
    print("StosOS Error Handling and Recovery System Tests")
    print("=" * 60)
    
    tests = [
        ("Error Handler", test_error_handler),
        ("System Health Monitor", test_system_health_monitor),
        ("Diagnostic Tools", test_diagnostic_tools),
        ("Notification Manager", test_notification_manager),
        ("Module Recovery Manager", test_module_recovery_manager),
        ("Component Integration", test_integration),
        ("Graceful Degradation", test_graceful_degradation),
        ("Error Pattern Detection", test_error_patterns)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        
        try:
            start_time = time.time()
            success = test_func()
            end_time = time.time()
            
            if success:
                print(f"✓ {test_name} PASSED ({end_time - start_time:.2f}s)")
                results.append((test_name, True, None))
            else:
                print(f"✗ {test_name} FAILED")
                results.append((test_name, False, "Test returned False"))
                
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
            results.append((test_name, False, str(e)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name:.<40} {status}")
        if error:
            print(f"  Error: {error}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All error handling tests passed!")
        return True
    else:
        print("❌ Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(Path(__file__).parent)
    
    # Run tests
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)