#!/usr/bin/env python3
"""
StosOS Power Management System
Handles display brightness control, idle detection, and power state transitions
"""

import os
import subprocess
import threading
import time
from enum import Enum
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from kivy.clock import Clock
from kivy.event import EventDispatcher

# Logger will be passed as parameter to avoid circular imports
from .error_handler import error_handler, ErrorType, ErrorSeverity

# Logger will be set during initialization


class PowerState(Enum):
    """Power management states"""
    ACTIVE = "active"      # 100% brightness, fully responsive
    DIMMED = "dimmed"      # 20% brightness, still responsive
    SLEEP = "sleep"        # 0% brightness, display off
    WAKE = "wake"          # Transitioning from sleep to active


@dataclass
class PowerConfig:
    """Power management configuration"""
    dim_timeout: float = 30.0      # Seconds before dimming
    sleep_timeout: float = 60.0    # Seconds before sleep
    active_brightness: int = 100   # Active brightness percentage
    dimmed_brightness: int = 20    # Dimmed brightness percentage
    sleep_brightness: int = 0      # Sleep brightness percentage
    wake_sensitivity: float = 0.1  # Touch sensitivity for wake
    enable_voice_wake: bool = True # Enable voice activation wake
    enable_network_wake: bool = True # Enable network command wake


class PowerManager(EventDispatcher):
    """
    Manages display power states, brightness control, and idle detection
    
    Features:
    - Automatic brightness dimming after idle timeout
    - Display sleep mode with touch wake
    - Voice activation wake support
    - Network command wake support
    - Smooth brightness transitions
    - Power state event notifications
    """
    
    __events__ = ('on_power_state_change', 'on_brightness_change', 'on_wake_event')
    
    def __init__(self, config: Optional[PowerConfig] = None, logger=None):
        super().__init__()
        self.config = config or PowerConfig()
        self.current_state = PowerState.ACTIVE
        self.current_brightness = self.config.active_brightness
        self.last_activity_time = time.time()
        
        # Set logger (use provided logger or create a basic one)
        if logger:
            self.logger = logger
        else:
            import logging
            self.logger = logging.getLogger(__name__)
        
        # Threading and timing
        self._monitor_thread = None
        self._monitor_running = False
        self._brightness_lock = threading.Lock()
        self._state_lock = threading.Lock()
        
        # Touch event handling
        self._touch_handlers = []
        self._voice_wake_callback = None
        self._network_wake_callback = None
        
        # Brightness control method detection
        self._brightness_method = self._detect_brightness_method()
        
        # Statistics and monitoring
        self._state_history = []
        self._wake_events = []
        
        self.logger.info("PowerManager initialized")
    
    def start_monitoring(self):
        """Start power management monitoring"""
        try:
            if self._monitor_running:
                self.logger.warning("Power monitoring already running")
                return
            
            self._monitor_running = True
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="PowerManager-Monitor"
            )
            self._monitor_thread.start()
            
            # Set initial state
            self._set_power_state(PowerState.ACTIVE)
            self._set_brightness(self.config.active_brightness)
            
            self.logger.info("Power management monitoring started")
            
        except Exception as e:
            error_handler.handle_error(
                e, "Power manager start", ErrorType.SYSTEM, ErrorSeverity.HIGH
            )
    
    def stop_monitoring(self):
        """Stop power management monitoring"""
        try:
            self._monitor_running = False
            
            if self._monitor_thread and self._monitor_thread.is_alive():
                self._monitor_thread.join(timeout=2.0)
            
            # Restore full brightness on shutdown
            self._set_brightness(self.config.active_brightness)
            
            self.logger.info("Power management monitoring stopped")
            
        except Exception as e:
            error_handler.handle_error(
                e, "Power manager stop", ErrorType.SYSTEM, ErrorSeverity.MEDIUM
            )
    
    def register_touch_handler(self, handler: Callable):
        """Register a touch event handler for wake functionality"""
        if handler not in self._touch_handlers:
            self._touch_handlers.append(handler)
            self.logger.debug("Touch handler registered")
    
    def unregister_touch_handler(self, handler: Callable):
        """Unregister a touch event handler"""
        if handler in self._touch_handlers:
            self._touch_handlers.remove(handler)
            self.logger.debug("Touch handler unregistered")
    
    def set_voice_wake_callback(self, callback: Callable):
        """Set callback for voice activation wake"""
        self._voice_wake_callback = callback
        self.logger.debug("Voice wake callback set")
    
    def set_network_wake_callback(self, callback: Callable):
        """Set callback for network command wake"""
        self._network_wake_callback = callback
        self.logger.debug("Network wake callback set")
    
    def on_user_activity(self):
        """Called when user activity is detected"""
        try:
            self.last_activity_time = time.time()
            
            # If we're not in active state, wake up
            if self.current_state != PowerState.ACTIVE:
                self.wake_display("user_activity")
            
        except Exception as e:
            error_handler.handle_error(
                e, "User activity handling", ErrorType.SYSTEM, ErrorSeverity.LOW
            )
    
    def on_touch_event(self, touch_data: Dict[str, Any]):
        """Handle touch events for wake functionality"""
        try:
            # Record wake event
            self._record_wake_event("touch", touch_data)
            
            # Trigger user activity
            self.on_user_activity()
            
            # Notify touch handlers
            for handler in self._touch_handlers:
                try:
                    handler(touch_data)
                except Exception as e:
                    self.logger.error(f"Touch handler error: {e}")
            
        except Exception as e:
            error_handler.handle_error(
                e, "Touch event handling", ErrorType.SYSTEM, ErrorSeverity.LOW
            )
    
    def wake_display(self, source: str = "manual"):
        """Wake the display from any power state"""
        try:
            if self.current_state == PowerState.ACTIVE:
                return  # Already active
            
            self.logger.info(f"Waking display from {self.current_state.value} (source: {source})")
            
            # Record wake event
            self._record_wake_event(source)
            
            # For testing or when no Kivy app is running, do immediate transition
            try:
                from kivy.app import App
                app = App.get_running_app()
                use_async = app is not None
            except:
                use_async = False
            
            if use_async:
                # Async transition for live app
                with self._state_lock:
                    self._set_power_state(PowerState.WAKE)
                
                Clock.schedule_once(
                    lambda dt: self._complete_wake_transition(),
                    0.1
                )
            else:
                # Immediate transition for testing
                with self._state_lock:
                    self._set_power_state(PowerState.ACTIVE)
                    self._set_brightness(self.config.active_brightness)
                    self.last_activity_time = time.time()
            
            # Dispatch wake event
            self.dispatch('on_wake_event', source)
            
        except Exception as e:
            error_handler.handle_error(
                e, "Display wake", ErrorType.SYSTEM, ErrorSeverity.MEDIUM
            )
    
    def force_sleep(self):
        """Force display into sleep mode"""
        try:
            with self._state_lock:
                self.logger.info("Forcing display sleep")
                self._set_power_state(PowerState.SLEEP)
                self._set_brightness(self.config.sleep_brightness)
            
        except Exception as e:
            error_handler.handle_error(
                e, "Force sleep", ErrorType.SYSTEM, ErrorSeverity.MEDIUM
            )
    
    def set_brightness(self, brightness: int):
        """Manually set display brightness (0-100)"""
        try:
            brightness = max(0, min(100, brightness))
            self._set_brightness(brightness)
            self.logger.info(f"Brightness manually set to {brightness}%")
            
        except Exception as e:
            error_handler.handle_error(
                e, "Manual brightness set", ErrorType.SYSTEM, ErrorSeverity.LOW
            )
    
    def get_power_state(self) -> PowerState:
        """Get current power state"""
        return self.current_state
    
    def get_brightness(self) -> int:
        """Get current brightness level"""
        return self.current_brightness
    
    def get_idle_time(self) -> float:
        """Get seconds since last user activity"""
        return time.time() - self.last_activity_time
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get power management statistics"""
        return {
            'current_state': self.current_state.value,
            'current_brightness': self.current_brightness,
            'idle_time': self.get_idle_time(),
            'state_history': self._state_history[-10:],  # Last 10 state changes
            'wake_events': self._wake_events[-20:],      # Last 20 wake events
            'brightness_method': self._brightness_method
        }
    
    # Event handlers (must be implemented for EventDispatcher)
    def on_power_state_change(self, old_state: PowerState, new_state: PowerState):
        """Called when power state changes"""
        pass
    
    def on_brightness_change(self, old_brightness: int, new_brightness: int):
        """Called when brightness changes"""
        pass
    
    def on_wake_event(self, source: str):
        """Called when wake event occurs"""
        pass
    
    # Private methods
    
    def _monitor_loop(self):
        """Main monitoring loop (runs in separate thread)"""
        self.logger.debug("Power monitoring loop started")
        
        while self._monitor_running:
            try:
                idle_time = self.get_idle_time()
                
                with self._state_lock:
                    if self.current_state == PowerState.ACTIVE:
                        if idle_time >= self.config.dim_timeout:
                            self._set_power_state(PowerState.DIMMED)
                            Clock.schedule_once(
                                lambda dt: self._set_brightness(self.config.dimmed_brightness),
                                0
                            )
                    
                    elif self.current_state == PowerState.DIMMED:
                        if idle_time >= self.config.sleep_timeout:
                            self._set_power_state(PowerState.SLEEP)
                            Clock.schedule_once(
                                lambda dt: self._set_brightness(self.config.sleep_brightness),
                                0
                            )
                
                # Check for voice wake (if enabled)
                if (self.config.enable_voice_wake and 
                    self._voice_wake_callback and 
                    self.current_state in [PowerState.DIMMED, PowerState.SLEEP]):
                    
                    try:
                        if self._voice_wake_callback():
                            Clock.schedule_once(
                                lambda dt: self.wake_display("voice"),
                                0
                            )
                    except Exception as e:
                        self.logger.debug(f"Voice wake check error: {e}")
                
                # Check for network wake (if enabled)
                if (self.config.enable_network_wake and 
                    self._network_wake_callback and 
                    self.current_state in [PowerState.DIMMED, PowerState.SLEEP]):
                    
                    try:
                        if self._network_wake_callback():
                            Clock.schedule_once(
                                lambda dt: self.wake_display("network"),
                                0
                            )
                    except Exception as e:
                        self.logger.debug(f"Network wake check error: {e}")
                
                # Sleep for monitoring interval
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Power monitoring loop error: {e}")
                time.sleep(5.0)  # Longer sleep on error
        
        self.logger.debug("Power monitoring loop stopped")
    
    def _set_power_state(self, new_state: PowerState):
        """Set power state and record history"""
        old_state = self.current_state
        
        if old_state != new_state:
            self.current_state = new_state
            
            # Record state change
            self._state_history.append({
                'timestamp': datetime.now().isoformat(),
                'old_state': old_state.value,
                'new_state': new_state.value,
                'idle_time': self.get_idle_time()
            })
            
            # Keep only recent history
            if len(self._state_history) > 100:
                self._state_history = self._state_history[-50:]
            
            self.logger.info(f"Power state changed: {old_state.value} -> {new_state.value}")
            
            # Dispatch event
            self.dispatch('on_power_state_change', old_state, new_state)
    
    def _set_brightness(self, brightness: int):
        """Set display brightness using detected method"""
        try:
            with self._brightness_lock:
                old_brightness = self.current_brightness
                brightness = max(0, min(100, brightness))
                
                # Always update internal brightness value
                self.current_brightness = brightness
                
                # Try to set actual hardware brightness
                try:
                    if self._brightness_method == "rpi_backlight":
                        self._set_brightness_rpi_backlight(brightness)
                    elif self._brightness_method == "xrandr":
                        self._set_brightness_xrandr(brightness)
                    elif self._brightness_method == "ddcutil":
                        self._set_brightness_ddcutil(brightness)
                    else:
                        self.logger.debug(f"No brightness control method available, tracking internally only")
                except Exception as hw_error:
                    self.logger.warning(f"Hardware brightness control failed: {hw_error}")
                
                if old_brightness != brightness:
                    self.logger.debug(f"Brightness changed: {old_brightness}% -> {brightness}%")
                    self.dispatch('on_brightness_change', old_brightness, brightness)
            
        except Exception as e:
            error_handler.handle_error(
                e, "Brightness control", ErrorType.SYSTEM, ErrorSeverity.MEDIUM
            )
    
    def _detect_brightness_method(self) -> str:
        """Detect available brightness control method"""
        try:
            # Check for Raspberry Pi backlight control
            if os.path.exists("/sys/class/backlight/rpi_backlight/brightness"):
                self.logger.info("Using Raspberry Pi backlight control")
                return "rpi_backlight"
            
            # Check for xrandr
            try:
                subprocess.run(["xrandr", "--version"], 
                             capture_output=True, check=True, timeout=5)
                self.logger.info("Using xrandr brightness control")
                return "xrandr"
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            # Check for ddcutil
            try:
                subprocess.run(["ddcutil", "--version"], 
                             capture_output=True, check=True, timeout=5)
                self.logger.info("Using ddcutil brightness control")
                return "ddcutil"
            except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                pass
            
            self.logger.warning("No brightness control method detected")
            return "none"
            
        except Exception as e:
            self.logger.error(f"Error detecting brightness method: {e}")
            return "none"
    
    def _set_brightness_rpi_backlight(self, brightness: int):
        """Set brightness using Raspberry Pi backlight control"""
        try:
            # Convert percentage to actual value (0-255)
            actual_brightness = int((brightness / 100.0) * 255)
            
            with open("/sys/class/backlight/rpi_backlight/brightness", "w") as f:
                f.write(str(actual_brightness))
            
        except Exception as e:
            raise Exception(f"RPi backlight control failed: {e}")
    
    def _set_brightness_xrandr(self, brightness: int):
        """Set brightness using xrandr"""
        try:
            # Convert percentage to xrandr brightness (0.0-1.0)
            xrandr_brightness = brightness / 100.0
            
            # Get primary display
            result = subprocess.run(
                ["xrandr", "--listmonitors"],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Extract display name from first monitor
                    display_line = lines[1]
                    display_name = display_line.split()[-1]
                    
                    # Set brightness
                    subprocess.run([
                        "xrandr", "--output", display_name, 
                        "--brightness", str(xrandr_brightness)
                    ], check=True, timeout=5)
                else:
                    raise Exception("No displays found")
            else:
                raise Exception("Failed to list displays")
            
        except Exception as e:
            raise Exception(f"xrandr brightness control failed: {e}")
    
    def _set_brightness_ddcutil(self, brightness: int):
        """Set brightness using ddcutil"""
        try:
            subprocess.run([
                "ddcutil", "setvcp", "10", str(brightness)
            ], check=True, timeout=10)
            
        except Exception as e:
            raise Exception(f"ddcutil brightness control failed: {e}")
    
    def _complete_wake_transition(self):
        """Complete the wake transition to active state"""
        try:
            self.logger.debug("Completing wake transition...")
            with self._state_lock:
                self.logger.debug("Acquired state lock, setting to ACTIVE")
                self._set_power_state(PowerState.ACTIVE)
                self._set_brightness(self.config.active_brightness)
                self.last_activity_time = time.time()
                self.logger.debug("Wake transition completed")
            
        except Exception as e:
            self.logger.error(f"Wake transition completion error: {e}")
            error_handler.handle_error(
                e, "Wake transition completion", ErrorType.SYSTEM, ErrorSeverity.MEDIUM
            )
    
    def _record_wake_event(self, source: str, data: Optional[Dict] = None):
        """Record a wake event for statistics"""
        wake_event = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'previous_state': self.current_state.value,
            'idle_time': self.get_idle_time(),
            'data': data or {}
        }
        
        self._wake_events.append(wake_event)
        
        # Keep only recent events
        if len(self._wake_events) > 200:
            self._wake_events = self._wake_events[-100:]
        
        self.logger.debug(f"Wake event recorded: {source}")


# Global power manager instance (will be initialized with proper logger in main.py)
import logging
power_manager = PowerManager(logger=logging.getLogger(__name__))