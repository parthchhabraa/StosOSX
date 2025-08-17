#!/usr/bin/env python3
"""
StosOS API Configuration Setup Script

This script helps you securely configure all API credentials for StosOS.
Supports: Spotify, Google Calendar, Google Assistant, OpenAI, and Alexa.
"""

import json
import os
import sys
from pathlib import Path
import getpass

def load_config():
    """Load existing configuration"""
    project_root = Path(__file__).parent
    config_file = project_root / "config" / "stosos_config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f), config_file
    else:
        print("❌ Configuration file not found!")
        print(f"Expected: {config_file}")
        return None, config_file

def save_config(config, config_file):
    """Save configuration securely"""
    try:
        # Ensure config directory exists
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Set secure file permissions
        os.chmod(config_file, 0o600)
        
        print(f"✅ Configuration saved to: {config_file}")
        print("🔒 File permissions set to 600 (owner read/write only)")
        return True
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False

def setup_spotify(config):
    """Setup Spotify API credentials"""
    print("\n" + "=" * 50)
    print("🎵 SPOTIFY API SETUP")
    print("=" * 50)
    
    spotify_config = config.get('spotify', {})
    
    print("\nCurrent Spotify configuration:")
    print(f"Client ID: {spotify_config.get('client_id', 'Not set')}")
    print(f"Client Secret: {'Set' if spotify_config.get('client_secret') else 'Not set'}")
    
    setup = input("\nSetup Spotify? (y/n): ").lower().strip()
    if setup != 'y':
        return config
    
    print("\nInstructions:")
    print("1. Go to https://developer.spotify.com/dashboard/")
    print("2. Create an app or use existing one")
    print("3. Add redirect URI: http://127.0.0.1:8080/callback")
    print("4. Copy your Client ID and Client Secret")
    
    client_id = input("\nEnter Spotify Client ID: ").strip()
    client_secret = getpass.getpass("Enter Spotify Client Secret: ").strip()
    
    if client_id and client_secret:
        config['spotify'] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "http://127.0.0.1:8080/callback",
            "scope": "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private user-read-recently-played",
            "enabled": True
        }
        print("✅ Spotify configuration updated")
    else:
        print("❌ Invalid credentials, skipping Spotify setup")
    
    return config

def setup_google_calendar(config):
    """Setup Google Calendar API credentials"""
    print("\n" + "=" * 50)
    print("📅 GOOGLE CALENDAR API SETUP")
    print("=" * 50)
    
    google_config = config.get('google_calendar', {})
    
    print("\nCurrent Google Calendar configuration:")
    print(f"Client ID: {google_config.get('client_id', 'Not set')}")
    print(f"Client Secret: {'Set' if google_config.get('client_secret') else 'Not set'}")
    
    setup = input("\nSetup Google Calendar? (y/n): ").lower().strip()
    if setup != 'y':
        return config
    
    print("\nInstructions:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a project or select existing one")
    print("3. Enable Google Calendar API")
    print("4. Create OAuth 2.0 credentials (Desktop application)")
    print("5. Add redirect URI: http://localhost:8080/callback")
    
    client_id = input("\nEnter Google Client ID: ").strip()
    client_secret = getpass.getpass("Enter Google Client Secret: ").strip()
    
    if client_id and client_secret:
        config['google_calendar'] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "http://localhost:8080/callback",
            "scopes": ["https://www.googleapis.com/auth/calendar"],
            "enabled": True
        }
        print("✅ Google Calendar configuration updated")
    else:
        print("❌ Invalid credentials, skipping Google Calendar setup")
    
    return config

def setup_openai(config):
    """Setup OpenAI API credentials"""
    print("\n" + "=" * 50)
    print("🤖 OPENAI API SETUP")
    print("=" * 50)
    
    openai_config = config.get('openai', {})
    
    print("\nCurrent OpenAI configuration:")
    print(f"API Key: {'Set' if openai_config.get('api_key') else 'Not set'}")
    
    setup = input("\nSetup OpenAI? (y/n): ").lower().strip()
    if setup != 'y':
        return config
    
    print("\nInstructions:")
    print("1. Go to https://platform.openai.com/")
    print("2. Create account or log in")
    print("3. Go to API Keys section")
    print("4. Create new secret key")
    
    api_key = getpass.getpass("\nEnter OpenAI API Key: ").strip()
    
    if api_key:
        config['openai'] = {
            "api_key": api_key,
            "model": "gpt-3.5-turbo",
            "max_tokens": 150,
            "temperature": 0.7,
            "enabled": True
        }
        print("✅ OpenAI configuration updated")
    else:
        print("❌ Invalid API key, skipping OpenAI setup")
    
    return config

def setup_alexa(config):
    """Setup Alexa Voice Service credentials"""
    print("\n" + "=" * 50)
    print("🗣️ ALEXA VOICE SERVICE SETUP")
    print("=" * 50)
    
    alexa_config = config.get('alexa', {})
    
    print("\nCurrent Alexa configuration:")
    print(f"Client ID: {alexa_config.get('client_id', 'Not set')}")
    print(f"Client Secret: {'Set' if alexa_config.get('client_secret') else 'Not set'}")
    
    setup = input("\nSetup Alexa Voice Service? (y/n): ").lower().strip()
    if setup != 'y':
        return config
    
    print("\nInstructions:")
    print("1. Go to https://developer.amazon.com/")
    print("2. Create account or log in")
    print("3. Go to Alexa Voice Service")
    print("4. Create new product (Device with Alexa Built-in)")
    print("5. Note Product ID, Client ID, and Client Secret")
    
    client_id = input("\nEnter Alexa Client ID: ").strip()
    client_secret = getpass.getpass("Enter Alexa Client Secret: ").strip()
    product_id = input("Enter Alexa Product ID: ").strip()
    
    if client_id and client_secret and product_id:
        config['alexa'] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "product_id": product_id,
            "redirect_uri": "http://localhost:3000/callback",
            "enabled": True
        }
        print("✅ Alexa configuration updated")
    else:
        print("❌ Invalid credentials, skipping Alexa setup")
    
    return config

def verify_setup(config):
    """Verify API setup"""
    print("\n" + "=" * 50)
    print("🔍 VERIFICATION")
    print("=" * 50)
    
    services = {
        'Spotify': config.get('spotify', {}).get('enabled', False),
        'Google Calendar': config.get('google_calendar', {}).get('enabled', False),
        'OpenAI': config.get('openai', {}).get('enabled', False),
        'Alexa': config.get('alexa', {}).get('enabled', False),
        'Voice Assistant': config.get('voice_assistant', {}).get('enabled', False)
    }
    
    print("\nConfigured services:")
    for service, enabled in services.items():
        status = "✅ Enabled" if enabled else "❌ Disabled"
        print(f"  {service}: {status}")
    
    enabled_count = sum(services.values())
    print(f"\nTotal enabled services: {enabled_count}/5")
    
    if enabled_count > 0:
        print("\n🎉 Setup complete! You can now:")
        if services['Spotify']:
            print("  🎵 Control Spotify with voice commands")
        if services['Google Calendar']:
            print("  📅 Manage calendar events")
        if services['OpenAI']:
            print("  🤖 Use advanced AI features")
        if services['Alexa']:
            print("  🗣️ Control Alexa devices")
        if services['Voice Assistant']:
            print("  🎤 Use 'Stos' wake word for voice control")
        
        print(f"\nNext steps:")
        print("1. Run StosOS: python main.py")
        print("2. Complete OAuth flows in browser")
        print("3. Start using voice commands!")
    else:
        print("\n⚠️ No services configured. Run setup again to configure APIs.")

def main():
    """Main setup function"""
    print("StosOS API Configuration Setup")
    print("=" * 60)
    print("This script will help you configure API credentials for:")
    print("🎵 Spotify - Music control")
    print("📅 Google Calendar - Calendar integration")
    print("🤖 OpenAI - Advanced AI features")
    print("🗣️ Alexa - Voice service integration")
    print("🎤 Voice Assistant - Built-in voice control")
    
    # Load existing config
    config, config_file = load_config()
    if config is None:
        return
    
    print(f"\nConfiguration file: {config_file}")
    
    # Setup services
    while True:
        print("\n" + "=" * 50)
        print("SELECT SERVICE TO CONFIGURE")
        print("=" * 50)
        print("1. Spotify")
        print("2. Google Calendar")
        print("3. OpenAI")
        print("4. Alexa Voice Service")
        print("5. Save and Exit")
        print("6. Exit without saving")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            config = setup_spotify(config)
        elif choice == '2':
            config = setup_google_calendar(config)
        elif choice == '3':
            config = setup_openai(config)
        elif choice == '4':
            config = setup_alexa(config)
        elif choice == '5':
            if save_config(config, config_file):
                verify_setup(config)
            break
        elif choice == '6':
            print("Exiting without saving changes.")
            break
        else:
            print("Invalid choice. Please select 1-6.")

if __name__ == "__main__":
    main()