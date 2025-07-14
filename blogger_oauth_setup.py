#!/usr/bin/env python3
"""
Google Blogger OAuth Setup Helper

This script helps you complete the Google Blogger OAuth setup process.
Run this after configuring BLOGGER_CLIENT_ID, BLOGGER_CLIENT_SECRET, and BLOGGER_BLOG_ID in your .env file.
"""

import os
from pathlib import Path

# Load .env file manually
env_file = Path('.env')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from solana_bot_tournament.blog_publisher import BloggerPublisher

def main():
    print("Google Blogger OAuth Setup Helper")
    print("=" * 40)
    
    publisher = BloggerPublisher()
    
    if not publisher.is_configured():
        print("[ERROR] Blogger OAuth not configured.")
        print("Please set these environment variables in your .env file:")
        print("- BLOGGER_CLIENT_ID")
        print("- BLOGGER_CLIENT_SECRET")
        print("- BLOGGER_BLOG_ID")
        print()
        print("Setup instructions:")
        print("1. Go to: https://console.developers.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable the Blogger API v3")
        print("4. Create OAuth 2.0 credentials")
        print("5. Find your Blog ID from your Blogger dashboard URL")
        return
    
    print(f"[OK] Client ID: {publisher.client_id}")
    print(f"[OK] Blog ID: {publisher.blog_id}")
    print(f"[OK] Client Secret: {'*' * len(publisher.client_secret)}")
    
    # Check if we already have a token
    token_file = Path("blogger_token.txt")
    if token_file.exists():
        print(f"\n[OK] Access token found in {token_file}")
        print("Blogger publishing should work!")
        return
    
    print("\n[INFO] No access token found. Starting OAuth flow...")
    print("\nStep 1: Visit the authorization URL")
    auth_url = publisher.get_authorization_url()
    print(f"URL: {auth_url}")
    
    print("\nStep 2: Sign in to your Google account and click 'Allow'")
    print("Step 3: Copy the authorization code from the page")
    code = input("Enter the authorization code: ").strip()
    
    if not code:
        print("[ERROR] No authorization code provided. Exiting.")
        return
    
    print("\nStep 4: Exchanging code for access token...")
    result = publisher.exchange_code_for_token(code)
    
    if result["success"]:
        print("[OK] Access token saved successfully!")
        print("Blogger publishing is now configured and ready to use.")
    else:
        print(f"[ERROR] Failed to get access token: {result['error']}")
        print("Please check your authorization code and try again.")

if __name__ == "__main__":
    main()