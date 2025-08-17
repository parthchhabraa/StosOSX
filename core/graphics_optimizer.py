"""
Graphics Optimizer for StosOS - Raspberry Pi 4 GPU Optimization

This module provides graphics rendering optimization, animation performance
tuning, and frame rate management specifically for Raspberry Pi 4 hardware.
"""

import time
import threading
from typing import Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass
from collections import deque
import weakref

try:
    from kivy.clock import Clock
    from kivy.graphics import PushMatrix, PopMatrix, Scale, Translate
    from kivy.animation import Animation
    from kivy.cache import Cache
    KIVY_AVAILABLE = True
except ImportError:
    # Mock Kivy components for testing without Kivy
    KIVY_AVAILABLE = False
    
    class MockClock:
        @staticmethod
        def schedule_once(func, timeout):
            return None
    
    class MockAnimation:
        def __init__(self, **kwargs):
            self._widgets = []
        
        def stop_all(self, widget=None):
            pass
        
        def bind(self, **kwargs):
            pass
    
    class MockCache:
        _cache = {}
        
        @classmethod
        def register(cls, name, **kwargs):
            cls._cache[name] = {}
        
        @classmethod
        def get(cls, name, key):
            return cls._cache.get(name, {}).get(key)
        
        @classmethod
        def append(cls, name, key, value):
            if name not in cls._cache:
                cls._cache[name] = {}
            cls._cache[name][key] = value
        
        @classmethod
        def remove(cls, name):
            if name in cls._cache:
                del cls._cache[name]
    
    Clock = MockClock()
    Animation = MockAnimation
    Cache = MockCache

from .logger import stosos_logger


@dataclass
class RenderingStats:
    """Statistics for rendering performance"""
    frame_count: int = 0
    total_render_time: float = 0.0
    avg_fps: float = 0.0
    dropped_frames: int = 0
    last_frame_time: float = 0.0


class FrameRateManager:
    """Manages frame rate and rendering performance"""
    
    def __init__(self, logger, target_fps: float = 30.0):
        self.logger = logger
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        
        self._frame_times = deque(maxlen=60)  # Keep last 60 frame times
        self._last_frame_time = time.time()
        self._stats = RenderingStats()
        
        # Adaptive quality settings
        self._quality_level = 1.0  # 0.5 = low, 1.0 = normal, 1.5 = high
        self._auto_adjust = True
        
        # Performance callbacks
        self._frame_callbacks: List[Callable[[float], None]] = []
    
    def start_frame(self) -> float:
        """Mark the start of a frame, return frame time"""
        current_time = time.time()
        frame_time = current_time - self._last_frame_time
        self._last_frame_time = current_time
        
        self._frame_times.append(frame_time * 1000)  # Convert to ms
        self._update_stats(frame_time)
        
        # Auto-adjust quality if enabled
        if self._auto_adjust:
            self._adjust_quality()
        
        # Notify callbacks
        for callback in self._frame_callbacks:
            try:
                callback(frame_time)
            except Exception as e:
                self.logger.error(f"Frame callback error: {e}")
        
        return frame_time
    
    def add_frame_callback(self, callback: Callable[[float], None]):
        """Add callback to be called each frame"""
        self._frame_callbacks.append(callback)
    
    def get_current_fps(self) -> float:
        """Get current FPS"""
        if len(self._frame_times) < 2:
            return 0.0
        
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        return 1000.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def get_quality_level(self) -> float:
        """Get current quality level"""
        return self._quality_level
    
    def set_quality_level(self, level: float):
        """Set quality level (0.5 = low, 1.0 = normal, 1.5 = high)"""
        self._quality_level = max(0.5, min(1.5, level))
        self.logger.info(f"Graphics quality set to: {self._quality_level}")
    
    def enable_auto_adjust(self, enabled: bool):
        """Enable/disable automatic quality adjustment"""
        self._auto_adjust = enabled
    
    def _update_stats(self, frame_time: float):
        """Update rendering statistics"""
        self._stats.frame_count += 1
        self._stats.total_render_time += frame_time
        self._stats.last_frame_time = frame_time
        
        if frame_time > self.target_frame_time * 1.5:  # 50% over target
            self._stats.dropped_frames += 1
        
        # Calculate average FPS over last 60 frames
        if len(self._frame_times) >= 10:
            avg_frame_time = sum(list(self._frame_times)[-10:]) / 10
            self._stats.avg_fps = 1000.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def _adjust_quality(self):
        """Automatically adjust quality based on performance"""
        if len(self._frame_times) < 30:  # Need enough samples
            return
        
        current_fps = self.get_current_fps()
        
        # If FPS is too low, reduce quality
        if current_fps < self.target_fps * 0.8:  # 20% below target
            if self._quality_level > 0.5:
                self._quality_level = max(0.5, self._quality_level - 0.1)
                self.logger.info(f"Reduced quality to {self._quality_level:.1f} (FPS: {current_fps:.1f})")
        
        # If FPS is good, try to increase quality
        elif current_fps > self.target_fps * 1.1:  # 10% above target
            if self._quality_level < 1.5:
                self._quality_level = min(1.5, self._quality_level + 0.05)
                self.logger.debug(f"Increased quality to {self._quality_level:.1f} (FPS: {current_fps:.1f})")
    
    def get_stats(self) -> RenderingStats:
        """Get current rendering statistics"""
        return self._stats


class AnimationOptimizer:
    """Optimizes animations for better performance"""
    
    def __init__(self, logger, frame_manager: FrameRateManager):
        self.logger = logger
        self.frame_manager = frame_manager
        
        # Animation pools for reuse
        self._animation_pool: List[Animation] = []
        self._active_animations: Dict[str, Animation] = {}
        
        # Optimization settings
        self._max_concurrent_animations = 5
        self._animation_quality_scale = 1.0
    
    def create_optimized_animation(self, widget, duration: float = 1.0, 
                                 transition: str = 'out_cubic', **kwargs) -> Animation:
        """Create an optimized animation"""
        # Adjust duration based on quality level
        quality = self.frame_manager.get_quality_level()
        adjusted_duration = duration * (2.0 - quality)  # Faster at lower quality
        
        # Limit concurrent animations
        if len(self._active_animations) >= self._max_concurrent_animations:
            self._cleanup_finished_animations()
        
        # Reuse animation from pool if available
        if self._animation_pool:
            anim = self._animation_pool.pop()
            anim.stop_all(widget)
        else:
            anim = Animation(duration=adjusted_duration, transition=transition, **kwargs)
        
        # Track active animation
        anim_id = f"{id(widget)}_{time.time()}"
        self._active_animations[anim_id] = anim
        
        # Add completion callback to return to pool
        def on_complete(animation, widget):
            if anim_id in self._active_animations:
                del self._active_animations[anim_id]
            self._return_to_pool(animation)
        
        anim.bind(on_complete=on_complete)
        
        return anim
    
    def create_fade_animation(self, widget, target_opacity: float, 
                            duration: float = 0.3) -> Animation:
        """Create optimized fade animation"""
        return self.create_optimized_animation(
            widget, duration=duration, opacity=target_opacity
        )
    
    def create_slide_animation(self, widget, target_pos: Tuple[float, float], 
                             duration: float = 0.5) -> Animation:
        """Create optimized slide animation"""
        return self.create_optimized_animation(
            widget, duration=duration, pos=target_pos
        )
    
    def create_scale_animation(self, widget, target_scale: float, 
                             duration: float = 0.3) -> Animation:
        """Create optimized scale animation"""
        # Use transform instead of size for better performance
        return self.create_optimized_animation(
            widget, duration=duration, 
            size=(widget.size[0] * target_scale, widget.size[1] * target_scale)
        )
    
    def _cleanup_finished_animations(self):
        """Clean up finished animations"""
        finished = []
        for anim_id, anim in self._active_animations.items():
            if not hasattr(anim, '_widgets') or not anim._widgets:
                finished.append(anim_id)
        
        for anim_id in finished:
            if anim_id in self._active_animations:
                anim = self._active_animations.pop(anim_id)
                self._return_to_pool(anim)
    
    def _return_to_pool(self, animation: Animation):
        """Return animation to pool for reuse"""
        if len(self._animation_pool) < 10:  # Limit pool size
            animation.stop_all()
            self._animation_pool.append(animation)


class TextureManager:
    """Manages texture caching and optimization"""
    
    def __init__(self, logger):
        self.logger = logger
        
        # Configure Kivy cache for better performance
        Cache.register('stosos_textures', limit=50, timeout=300)  # 5 minutes
        Cache.register('stosos_images', limit=20, timeout=600)    # 10 minutes
        
        self._texture_refs: Dict[str, weakref.ref] = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def get_cached_texture(self, key: str, loader_func: Callable):
        """Get texture from cache or load it"""
        # Try cache first
        texture = Cache.get('stosos_textures', key)
        if texture:
            self._cache_hits += 1
            return texture
        
        # Load and cache
        try:
            texture = loader_func()
            Cache.append('stosos_textures', key, texture)
            self._cache_misses += 1
            return texture
        except Exception as e:
            self.logger.error(f"Failed to load texture {key}: {e}")
            return None
    
    def preload_textures(self, texture_specs: List[Tuple[str, Callable]]):
        """Preload textures in background"""
        def preload_worker():
            for key, loader in texture_specs:
                try:
                    self.get_cached_texture(key, loader)
                except Exception as e:
                    self.logger.error(f"Failed to preload texture {key}: {e}")
        
        threading.Thread(target=preload_worker, daemon=True).start()
    
    def clear_cache(self):
        """Clear texture cache"""
        Cache.remove('stosos_textures')
        Cache.remove('stosos_images')
        self.logger.info("Texture cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'hits': self._cache_hits,
            'misses': self._cache_misses,
            'hit_ratio': self._cache_hits / (self._cache_hits + self._cache_misses) 
                        if (self._cache_hits + self._cache_misses) > 0 else 0.0
        }


class RenderingOptimizer:
    """Optimizes rendering operations"""
    
    def __init__(self, logger):
        self.logger = logger
        self._render_batches: List[Callable] = []
        self._batch_timer = None
        
    def batch_render_operation(self, operation: Callable):
        """Add operation to render batch"""
        self._render_batches.append(operation)
        
        # Schedule batch execution
        if self._batch_timer:
            self._batch_timer.cancel()
        
        self._batch_timer = Clock.schedule_once(self._execute_batch, 0.016)  # ~60fps
    
    def _execute_batch(self, dt):
        """Execute batched render operations"""
        if not self._render_batches:
            return
        
        start_time = time.time()
        
        try:
            for operation in self._render_batches:
                operation()
        except Exception as e:
            self.logger.error(f"Batch render error: {e}")
        finally:
            self._render_batches.clear()
            self._batch_timer = None
        
        render_time = time.time() - start_time
        if render_time > 0.016:  # Longer than one frame
            self.logger.warning(f"Slow batch render: {render_time:.3f}s")


class GraphicsOptimizer:
    """Main graphics optimization system"""
    
    def __init__(self, logger, target_fps: float = 30.0):
        self.logger = logger
        
        self.frame_manager = FrameRateManager(logger, target_fps)
        self.animation_optimizer = AnimationOptimizer(logger, self.frame_manager)
        self.texture_manager = TextureManager(logger)
        self.rendering_optimizer = RenderingOptimizer(logger)
        
        # Register frame callback for performance monitoring
        self.frame_manager.add_frame_callback(self._on_frame)
        
        # Optimization settings
        self._vsync_enabled = True
        self._texture_filtering = True
        self._antialiasing = False  # Disabled for performance
    
    def initialize(self):
        """Initialize graphics optimization"""
        try:
            if KIVY_AVAILABLE:
                # Configure Kivy for better performance on Pi 4
                from kivy.config import Config
                
                # Disable multisampling for better performance
                Config.set('graphics', 'multisamples', '0')
                
                # Use OpenGL ES for Raspberry Pi
                if self._is_raspberry_pi():
                    Config.set('graphics', 'opengl_es2', '1')
            
            self.logger.info("Graphics optimization initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize graphics optimization: {e}")
    
    def optimize_for_raspberry_pi(self):
        """Apply Raspberry Pi specific optimizations"""
        try:
            # Reduce texture quality for better performance
            self.frame_manager.set_quality_level(0.8)
            
            if KIVY_AVAILABLE:
                # Enable aggressive caching
                Cache.register('kv_texture', limit=30, timeout=300)
            
            # Disable expensive effects
            self._antialiasing = False
            
            self.logger.info("Applied Raspberry Pi optimizations")
            
        except Exception as e:
            self.logger.error(f"Failed to apply Pi optimizations: {e}")
    
    def create_optimized_animation(self, widget, **kwargs) -> Animation:
        """Create performance-optimized animation"""
        return self.animation_optimizer.create_optimized_animation(widget, **kwargs)
    
    def batch_render(self, operation: Callable):
        """Add operation to render batch"""
        self.rendering_optimizer.batch_render_operation(operation)
    
    def get_performance_stats(self) -> Dict[str, any]:
        """Get comprehensive graphics performance statistics"""
        return {
            'rendering': self.frame_manager.get_stats().__dict__,
            'current_fps': self.frame_manager.get_current_fps(),
            'quality_level': self.frame_manager.get_quality_level(),
            'texture_cache': self.texture_manager.get_cache_stats(),
            'active_animations': len(self.animation_optimizer._active_animations)
        }
    
    def _on_frame(self, frame_time: float):
        """Called each frame for monitoring"""
        # Log performance issues
        if frame_time > 0.05:  # >50ms frame time
            self.logger.warning(f"Slow frame: {frame_time*1000:.1f}ms")
    
    def _is_raspberry_pi(self) -> bool:
        """Check if running on Raspberry Pi"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def cleanup(self):
        """Clean up graphics resources"""
        self.texture_manager.clear_cache()
        self.animation_optimizer._active_animations.clear()
        self.logger.info("Graphics resources cleaned up")