#!/usr/bin/env python3
"""
Quick Setup Script for StosOS

This script quickly configures the provided API credentials.
For security, you should run this once and then delete it.
"""

import json
import os
from pathlib import Path

def quick_setup():
    """Quick setup with provided credentials"""
    
    print("StosOS Quick Setup")
    print("=" * 40)
    
    # Configuration
    project_root = Path(__file__).parent
    config_file = project_root / "config" / "stosos_config.json"
    
    # Load existing config
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        print("❌ Configuration file not found!")
        return False
    
    print("Setting up API credentials...")
    
    # Spotify credentials (you provided)
    config['spotify'] = {
        "client_id": "515b520ddd7b4ed2a33fdd1091c9ef00",
        "client_secret": "PLACEHOLDER_FOR_SPOTIFY_SECRET",
        "redirect_uri": "http://127.0.0.1:8080/callback",
        "scope": "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private user-read-recently-played",
        "enabled": True
    }
    
    # Google Calendar credentials (you provided)
    config['google_calendar'] = {
        "client_id": "810084908386-0amsmo2lc9qp3gg6fuscnjsq3m8k5ig7.apps.googleusercontent.com",
        "client_secret": "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",
        "redirect_uri": "http://localhost:8080/callback",
        "scopes": ["https://www.googleapis.com/auth/calendar"],
        "enabled": True
    }
    
    # Voice Assistant (already configured)
    config['voice_assistant']['enabled'] = True
    
    # Save configuration
    try:
        # Ensure config directory exists
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure file permissions
        os.chmod(config_file, 0o600)
        
        print("✅ Configuration updated successfully!")
        print(f"📁 Config file: {config_file}")
        print("🔒 Secure permissions applied")
        
        print("\n📋 Configured Services:")
        print("✅ Spotify - Music control")
        print("✅ Google Calendar - Calendar integration") 
        print("✅ Voice Assistant - 'Stos' wake word")
        
        print("\n🚀 Next Steps:")
        print("1. Delete this script for security: rm quick_setup.py")
        print("2. Run StosOS: python main.py")
        print("3. Complete OAuth authentication in browser")
        print("4. Start using voice commands!")
        
        print("\n🎤 Try these voice commands:")
        print("  'Stos, play some music'")
        print("  'Stos, show my calendar'")
        print("  'Stos, what time is it'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def main():
    """Main function"""
    
    print("⚠️  SECURITY NOTICE:")
    print("This script contains API credentials and should be deleted after use.")
    print("Run this script only once to configure your APIs.")
    
    proceed = input("\nProceed with quick setup? (y/n): ").lower().strip()
    if proceed == 'y':
        if quick_setup():
            print("\n🔐 IMPORTANT: Delete this script now for security!")
            print("Command: rm quick_setup.py")
        else:
            print("❌ Setup failed")
    else:
        print("Setup cancelled")

if __name__ == "__main__":
    main()