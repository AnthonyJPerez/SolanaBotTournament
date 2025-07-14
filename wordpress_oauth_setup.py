#!/usr/bin/env python3
"""
WordPress OAuth Setup Helper

This script helps you complete the WordPress.com OAuth setup process.
Run this after configuring WORDPRESS_CLIENT_ID, WORDPRESS_CLIENT_SECRET, and WORDPRESS_SITE_URL in your .env file.
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

from solana_bot_tournament.blog_publisher import WordPressPublisher

def main():
    print("WordPress.com OAuth Setup Helper")
    print("=" * 40)
    
    publisher = WordPressPublisher()
    
    if not publisher.is_configured():
        print("[ERROR] WordPress OAuth not configured.")
        print("Please set these environment variables in your .env file:")
        print("- WORDPRESS_CLIENT_ID")
        print("- WORDPRESS_CLIENT_SECRET")
        print("- WORDPRESS_SITE_URL")
        return
    
    print(f"[OK] Client ID: {publisher.client_id}")
    print(f"[OK] Site URL: {publisher.site_url}")
    print(f"[OK] Client Secret: {'*' * len(publisher.client_secret)}")
    
    # Check if we already have a token
    token_file = Path("wordpress_token.txt")
    if token_file.exists():
        print(f"\n[OK] Access token found in {token_file}")
        print("WordPress publishing should work!")
        return
    
    print("\n[INFO] No access token found. Starting OAuth flow...")
    print("\nStep 1: Visit the authorization URL")
    auth_url = publisher.get_authorization_url()
    print(f"URL: {auth_url}")
    
    print("\nStep 2: After authorizing, you'll be redirected to:")
    print("https://localhost:8080/callback?code=AUTHORIZATION_CODE")
    
    print("\nStep 3: Copy the authorization code from the URL")
    code = input("Enter the authorization code: ").strip()
    
    if not code:
        print("[ERROR] No authorization code provided. Exiting.")
        return
    
    print("\nStep 4: Exchanging code for access token...")
    result = publisher.exchange_code_for_token(code)
    
    if result["success"]:
        print("[OK] Access token saved successfully!")
        print("WordPress publishing is now configured and ready to use.")
    else:
        print(f"[ERROR] Failed to get access token: {result['error']}")
        print("Please check your authorization code and try again.")

if __name__ == "__main__":
    main()