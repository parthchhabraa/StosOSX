#!/usr/bin/env python3
"""
Test script for Spotify Controller Module

This script tests the basic functionality of the Spotify controller module
including initialization, UI creation, and basic operations.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock Kivy before importing
sys.modules['kivy'] = Mock()
sys.modules['kivy.app'] = Mock()
sys.modules['kivy.uix'] = Mock()
sys.modules['kivy.uix.screenmanager'] = Mock()
sys.modules['kivy.uix.boxlayout'] = Mock()
sys.modules['kivy.uix.gridlayout'] = Mock()
sys.modules['kivy.uix.floatlayout'] = Mock()
sys.modules['kivy.clock'] = Mock()
sys.modules['kivy.metrics'] = Mock()
sys.modules['kivy.network'] = Mock()
sys.modules['kivy.network.urlrequest'] = Mock()

# Mock Spotipy
sys.modules['spotipy'] = Mock()
sys.modules['spotipy.oauth2'] = Mock()

from modules.spotify_controller import SpotifyController


class TestSpotifyController(unittest.TestCase):
    """Test cases for Spotify Controller module"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock dependencies
        self.mock_config_manager = Mock()
        self.mock_config_manager.get_config.return_value = {
            'spotify': {
                'client_id': 'test_client_id',
                'client_secret': 'test_client_secret',
                'redirect_uri': 'http://localhost:8080/callback'
            }
        }
        
        # Create controller instance
        with patch('modules.spotify_controller.ConfigManager', return_value=self.mock_config_manager):
            self.controller = SpotifyController()
    
    def test_module_initialization(self):
        """Test module basic properties"""
        self.assertEqual(self.controller.module_id, "spotify_controller")
        self.assertEqual(self.controller.display_name, "Spotify Controller")
        self.assertEqual(self.controller.icon, "music")
        self.assertFalse(self.controller._initialized)
    
    @patch('modules.spotify_controller.spotipy.Spotify')
    @patch('modules.spotify_controller.SpotifyOAuth')
    def test_spotify_client_initialization(self, mock_oauth, mock_spotify):
        """Test Spotify client initialization"""
        # Mock successful authentication
        mock_spotify_instance = Mock()
        mock_spotify_instance.current_user.return_value = {'display_name': 'Test User'}
        mock_spotify.return_value = mock_spotify_instance
        
        # Test initialization
        result = self.controller._initialize_spotify_client()
        
        self.assertTrue(result)
        self.assertIsNotNone(self.controller.spotify_client)
        mock_oauth.assert_called_once()
        mock_spotify.assert_called_once()
    
    def test_spotify_client_initialization_failure(self):
        """Test Spotify client initialization with missing credentials"""
        # Mock missing credentials
        self.mock_config_manager.get_config.return_value = {'spotify': {}}
        
        result = self.controller._initialize_spotify_client()
        
        self.assertFalse(result)
        self.assertIsNone(self.controller.spotify_client)
    
    def test_voice_command_handling(self):
        """Test voice command processing"""
        # Mock Spotify client
        self.controller.spotify_client = Mock()
        
        # Test play command
        result = self.controller.handle_voice_command("play music")
        self.assertTrue(result)
        
        # Test pause command
        result = self.controller.handle_voice_command("pause music")
        self.assertTrue(result)
        
        # Test next command
        result = self.controller.handle_voice_command("next song")
        self.assertTrue(result)
        
        # Test previous command
        result = self.controller.handle_voice_command("previous track")
        self.assertTrue(result)
        
        # Test volume commands
        result = self.controller.handle_voice_command("volume up")
        self.assertTrue(result)
        
        result = self.controller.handle_voice_command("volume down")
        self.assertTrue(result)
        
        # Test unrecognized command
        result = self.controller.handle_voice_command("unknown command")
        self.assertFalse(result)
    
    def test_playback_controls(self):
        """Test playback control methods"""
        # Mock Spotify client and current playback
        self.controller.spotify_client = Mock()
        self.controller.current_playback = {
            'is_playing': True,
            'device': {'volume_percent': 50}
        }
        
        # Test toggle playback (should pause when playing)
        self.controller._toggle_playback()
        self.controller.spotify_client.pause_playback.assert_called_once()
        
        # Test play music
        self.controller._play_music()
        self.controller.spotify_client.start_playback.assert_called()
        
        # Test pause music
        self.controller._pause_music()
        self.controller.spotify_client.pause_playback.assert_called()
        
        # Test next track
        self.controller._next_track()
        self.controller.spotify_client.next_track.assert_called_once()
        
        # Test previous track
        self.controller._previous_track()
        self.controller.spotify_client.previous_track.assert_called_once()
    
    def test_volume_adjustment(self):
        """Test volume adjustment"""
        # Mock Spotify client and current playback
        self.controller.spotify_client = Mock()
        self.controller.current_playback = {
            'device': {'volume_percent': 50}
        }
        
        # Test volume up
        self.controller._adjust_volume(10)
        self.controller.spotify_client.volume.assert_called_with(60)
        
        # Test volume down
        self.controller._adjust_volume(-20)
        self.controller.spotify_client.volume.assert_called_with(30)
        
        # Test volume bounds (should not go below 0 or above 100)
        self.controller.current_playback['device']['volume_percent'] = 5
        self.controller._adjust_volume(-10)
        self.controller.spotify_client.volume.assert_called_with(0)
        
        self.controller.current_playback['device']['volume_percent'] = 95
        self.controller._adjust_volume(10)
        self.controller.spotify_client.volume.assert_called_with(100)
    
    def test_device_selection(self):
        """Test device selection"""
        # Mock Spotify client
        self.controller.spotify_client = Mock()
        
        device_info = {'id': 'test_device_id', 'name': 'Test Device'}
        
        self.controller._select_device(device_info)
        self.controller.spotify_client.transfer_playback.assert_called_with('test_device_id', force_play=False)
    
    def test_track_playback(self):
        """Test playing specific tracks and playlists"""
        # Mock Spotify client
        self.controller.spotify_client = Mock()
        
        # Test play track
        track_info = {'uri': 'spotify:track:test_track_id'}
        self.controller._play_track(track_info)
        self.controller.spotify_client.start_playback.assert_called_with(uris=['spotify:track:test_track_id'])
        
        # Test play playlist
        playlist_info = {'uri': 'spotify:playlist:test_playlist_id'}
        self.controller._play_playlist(playlist_info)
        self.controller.spotify_client.start_playback.assert_called_with(context_uri='spotify:playlist:test_playlist_id')
    
    def test_data_updates(self):
        """Test data update methods"""
        # Mock Spotify client with sample data
        self.controller.spotify_client = Mock()
        
        # Mock current playback
        self.controller.spotify_client.current_playback.return_value = {
            'is_playing': True,
            'item': {
                'name': 'Test Track',
                'artists': [{'name': 'Test Artist'}],
                'album': {'name': 'Test Album'},
                'duration_ms': 180000
            },
            'progress_ms': 60000,
            'device': {'volume_percent': 75}
        }
        
        # Mock devices
        self.controller.spotify_client.devices.return_value = {
            'devices': [
                {'id': 'device1', 'name': 'Speaker 1', 'type': 'Speaker'},
                {'id': 'device2', 'name': 'Phone', 'type': 'Smartphone'}
            ]
        }
        
        # Mock playlists
        self.controller.spotify_client.current_user_playlists.return_value = {
            'items': [
                {'name': 'My Playlist', 'uri': 'spotify:playlist:1', 'tracks': {'total': 25}},
                {'name': 'Favorites', 'uri': 'spotify:playlist:2', 'tracks': {'total': 50}}
            ]
        }
        
        # Mock recently played
        self.controller.spotify_client.current_user_recently_played.return_value = {
            'items': [
                {'track': {'name': 'Recent Track 1', 'artists': [{'name': 'Artist 1'}]}},
                {'track': {'name': 'Recent Track 2', 'artists': [{'name': 'Artist 2'}]}}
            ]
        }
        
        # Test updates
        self.controller._update_current_playback()
        self.assertIsNotNone(self.controller.current_playback)
        self.assertIsNotNone(self.controller.current_track)
        
        self.controller._update_devices()
        self.assertEqual(len(self.controller.devices), 2)
        
        self.controller._update_playlists()
        self.assertEqual(len(self.controller.playlists), 2)
        
        self.controller._update_recently_played()
        self.assertEqual(len(self.controller.recently_played), 2)
    
    def test_module_status(self):
        """Test module status reporting"""
        status = self.controller.get_status()
        
        self.assertEqual(status['module_id'], 'spotify_controller')
        self.assertEqual(status['display_name'], 'Spotify Controller')
        self.assertEqual(status['icon'], 'music')
        self.assertFalse(status['initialized'])
        self.assertFalse(status['active'])
    
    def test_cleanup(self):
        """Test module cleanup"""
        # Set up some state
        self.controller.spotify_client = Mock()
        self.controller.update_timer = Mock()
        
        # Test cleanup
        self.controller.cleanup()
        
        self.assertIsNone(self.controller.spotify_client)
        self.controller.update_timer.cancel.assert_called_once()
        self.assertFalse(self.controller._initialized)
        self.assertFalse(self.controller._active)


def run_tests():
    """Run all tests"""
    print("Running Spotify Controller Module Tests...")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestSpotifyController)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print(f"Ran {result.testsRun} tests successfully")
    else:
        print("❌ Some tests failed!")
        print(f"Ran {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)