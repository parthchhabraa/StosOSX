#!/usr/bin/env python3
"""
Spotify Configuration Setup Script for StosOS

This script helps you securely configure your Spotify API credentials.
Run this script to set up your Spotify integration.
"""

import json
import os
import sys
from pathlib import Path

def setup_spotify_credentials():
    """Interactive setup for Spotify credentials"""
    
    print("=" * 60)
    print("StosOS Spotify Configuration Setup")
    print("=" * 60)
    
    # Get project root
    project_root = Path(__file__).parent
    config_file = project_root / "config" / "stosos_config.json"
    
    # Load existing config
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        print("❌ Configuration file not found!")
        print(f"Expected: {config_file}")
        return False
    
    print("\n📋 Current Spotify Configuration:")
    spotify_config = config.get('spotify', {})
    print(f"Client ID: {spotify_config.get('client_id', 'Not set')}")
    print(f"Client Secret: {'Set' if spotify_config.get('client_secret') else 'Not set'}")
    print(f"Redirect URI: {spotify_config.get('redirect_uri', 'Not set')}")
    
    print("\n🔧 Setting up Spotify credentials...")
    
    # Get Client ID
    current_client_id = spotify_config.get('client_id', '')
    if current_client_id:
        print(f"\nCurrent Client ID: {current_client_id}")
        use_current = input("Use current Client ID? (y/n): ").lower().strip()
        if use_current != 'y':
            client_id = input("Enter your Spotify Client ID: ").strip()
        else:
            client_id = current_client_id
    else:
        client_id = input("Enter your Spotify Client ID: ").strip()
    
    # Get Client Secret
    client_secret = input("Enter your Spotify Client Secret: ").strip()
    
    # Validate inputs
    if not client_id or not client_secret:
        print("❌ Both Client ID and Client Secret are required!")
        return False
    
    # Update configuration
    config['spotify']['client_id'] = client_id
    config['spotify']['client_secret'] = client_secret
    config['spotify']['redirect_uri'] = "http://127.0.0.1:8080/callback"
    config['spotify']['enabled'] = True
    
    # Save configuration
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure file permissions
        os.chmod(config_file, 0o600)
        
        print("\n✅ Spotify configuration saved successfully!")
        print(f"📁 Configuration file: {config_file}")
        print("\n🔒 File permissions set to 600 (owner read/write only)")
        
        print("\n📋 Final Configuration:")
        print(f"Client ID: {client_id}")
        print(f"Client Secret: {'*' * len(client_secret)}")
        print(f"Redirect URI: {config['spotify']['redirect_uri']}")
        
        print("\n🎵 Spotify integration is now configured!")
        print("You can now use voice commands like:")
        print("  - 'Stos, play some music'")
        print("  - 'Stos, pause music'")
        print("  - 'Stos, skip song'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def verify_spotify_setup():
    """Verify Spotify configuration"""
    
    print("\n🔍 Verifying Spotify setup...")
    
    try:
        # Import and test Spotify module
        sys.path.insert(0, str(Path(__file__).parent))
        
        from modules.spotify_controller import SpotifyControllerModule
        from core.config_manager import ConfigManager
        
        # Create config manager
        config_manager = ConfigManager()
        
        # Create Spotify module
        spotify_module = SpotifyControllerModule()
        
        # Test initialization (without actually connecting)
        print("✅ Spotify module imports successfully")
        print("✅ Configuration file is valid")
        
        # Check if credentials are set
        spotify_config = config_manager.get('spotify', {})
        
        if spotify_config.get('client_id') and spotify_config.get('client_secret'):
            print("✅ Spotify credentials are configured")
        else:
            print("❌ Spotify credentials are missing")
            return False
        
        print("\n🎉 Spotify setup verification complete!")
        print("\nNext steps:")
        print("1. Run StosOS: python main.py")
        print("2. Navigate to Spotify module")
        print("3. Complete OAuth authentication in browser")
        print("4. Start controlling your music with voice commands!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Main setup function"""
    
    print("Welcome to StosOS Spotify Setup!")
    print("\nThis script will help you configure Spotify integration.")
    print("Make sure you have:")
    print("1. Created a Spotify app at https://developer.spotify.com/dashboard/")
    print("2. Added redirect URI: http://127.0.0.1:8080/callback")
    print("3. Noted your Client ID and Client Secret")
    
    proceed = input("\nReady to proceed? (y/n): ").lower().strip()
    if proceed != 'y':
        print("Setup cancelled.")
        return
    
    # Setup credentials
    if setup_spotify_credentials():
        # Verify setup
        verify_spotify_setup()
    else:
        print("❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main()