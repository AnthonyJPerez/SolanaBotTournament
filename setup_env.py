#!/usr/bin/env python3
"""
Setup script for Solana Bot Tournament environment configuration.
Helps users configure their .env file with proper API keys.
"""
import os
import shutil
from pathlib import Path


def validate_solana_address(address: str) -> bool:
    """Basic validation for Solana address format."""
    if not address:
        return False
    # Solana addresses are base58 encoded, typically 32-44 characters
    # This is a basic check - more sophisticated validation could be added
    if len(address) < 32 or len(address) > 44:
        return False
    # Check for valid base58 characters (excluding 0, O, I, l)
    valid_chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    return all(c in valid_chars for c in address)


def setup_environment():
    """Interactive setup for environment variables."""
    print("Solana Bot Tournament - Environment Setup")
    print("=" * 50)
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    # Copy .env.example to .env if it doesn't exist
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("[OK] Created .env file from template")
        else:
            print("[ERROR] .env.example not found!")
            return False
    else:
        print("[WARNING] .env file already exists")
        overwrite = input("Do you want to reconfigure it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return False
    
    print("\nLet's configure your API keys:")
    print("You can skip any optional services by pressing Enter\n")
    
    # Configuration prompts
    configs = []
    
    # Required: Helius API
    print("HELIUS API (REQUIRED)")
    print("Get your API key from: https://www.helius.dev/")
    helius_key = input("Enter your Helius API key: ").strip()
    if helius_key:
        configs.append(f"HELIUS_API_KEY={helius_key}")
    else:
        print("[WARNING] Without Helius API key, only mock mode will work")
        configs.append("HELIUS_API_KEY=")
    
    # Optional: Telegram
    print("\nTELEGRAM ALERTS (Optional)")
    print("Create bot: https://core.telegram.org/bots#botfather")
    tg_token = input("Enter Telegram bot token (or press Enter to skip): ").strip()
    if tg_token:
        tg_chat = input("Enter Telegram chat ID: ").strip()
        configs.append(f"TELEGRAM_BOT_TOKEN={tg_token}")
        configs.append(f"TELEGRAM_CHAT_ID={tg_chat}")
    else:
        print("[INFO] Skipping Telegram configuration")
        configs.append("TELEGRAM_BOT_TOKEN=")
        configs.append("TELEGRAM_CHAT_ID=")
    
    # Optional: Twitter
    print("\nTWITTER POSTING (Optional)")
    print("Get API keys from: https://developer.twitter.com/")
    twitter_key = input("Enter Twitter API key (or press Enter to skip): ").strip()
    if twitter_key:
        twitter_secret = input("Enter Twitter API secret: ").strip()
        twitter_token = input("Enter Twitter access token: ").strip()
        twitter_token_secret = input("Enter Twitter access token secret: ").strip()
        
        configs.extend([
            f"TWITTER_API_KEY={twitter_key}",
            f"TWITTER_API_SECRET={twitter_secret}",
            f"TWITTER_ACCESS_TOKEN={twitter_token}",
            f"TWITTER_ACCESS_SECRET={twitter_token_secret}"
        ])
    else:
        print("[INFO] Skipping Twitter configuration")
        configs.extend([
            "TWITTER_API_KEY=",
            "TWITTER_API_SECRET=",
            "TWITTER_ACCESS_TOKEN=",
            "TWITTER_ACCESS_SECRET="
        ])
    
    # Required: Bot Wallet Addresses
    print("\\nBOT WALLET ADDRESSES (Required for real data)")
    print("Enter the Solana wallet addresses for each bot")
    print("These are public addresses used to track transactions")
    print("(Leave blank if you don't have a specific bot's address yet)")
    
    # Helper function to get and validate wallet address
    def get_wallet_address(bot_name: str) -> str:
        while True:
            addr = input(f"Enter {bot_name} bot wallet address: ").strip()
            if not addr:
                print(f"[INFO] Skipping {bot_name} wallet address")
                return ""
            if validate_solana_address(addr):
                print(f"[OK] Valid Solana address for {bot_name}")
                return addr
            else:
                print("[ERROR] Invalid Solana address format. Please try again.")
                print("Solana addresses are 32-44 characters long, base58 encoded")
                retry = input("Try again? (y/N): ").lower().strip()
                if retry != 'y':
                    return ""
    
    trojan_addr = get_wallet_address("Trojan")
    tradewiz_addr = get_wallet_address("TradeWiz") 
    frogbot_addr = get_wallet_address("FrogBot")
    
    configs.extend([
        f"TROJAN_WALLET_ADDRESS={trojan_addr}",
        f"TRADEWIZ_WALLET_ADDRESS={tradewiz_addr}",
        f"FROGBOT_WALLET_ADDRESS={frogbot_addr}"
    ])
    
    # Optional: Blog Publishing
    print("\\nBLOG PUBLISHING (Optional)")
    print("Configure any platforms you want to publish tournament reports to")
    print("You can skip all of these by pressing Enter")
    
    # Medium
    medium_token = input("Enter Medium access token (or press Enter to skip): ").strip()
    configs.append(f"MEDIUM_ACCESS_TOKEN={medium_token}")
    
    # Dev.to
    devto_key = input("Enter Dev.to API key (or press Enter to skip): ").strip()
    configs.append(f"DEVTO_API_KEY={devto_key}")
    
    # Hashnode
    hashnode_token = input("Enter Hashnode access token (or press Enter to skip): ").strip()
    if hashnode_token:
        hashnode_pub_id = input("Enter Hashnode publication ID: ").strip()
        configs.extend([
            f"HASHNODE_ACCESS_TOKEN={hashnode_token}",
            f"HASHNODE_PUBLICATION_ID={hashnode_pub_id}"
        ])
    else:
        configs.extend([
            "HASHNODE_ACCESS_TOKEN=",
            "HASHNODE_PUBLICATION_ID="
        ])
    
    # Blogger
    print("\\nGoogle Blogger OAuth setup:")
    print("1. Visit: https://console.developers.google.com/")
    print("2. Create project and enable Blogger API v3")
    print("3. Create OAuth 2.0 credentials")
    blogger_client_id = input("Enter Google OAuth Client ID (or press Enter to skip): ").strip()
    if blogger_client_id:
        blogger_client_secret = input("Enter Google OAuth Client Secret: ").strip()
        blogger_blog_id = input("Enter Blogger Blog ID (from your blog URL): ").strip()
        configs.extend([
            f"BLOGGER_CLIENT_ID={blogger_client_id}",
            f"BLOGGER_CLIENT_SECRET={blogger_client_secret}",
            f"BLOGGER_BLOG_ID={blogger_blog_id}"
        ])
        print("NOTE: Run 'python blogger_oauth_setup.py' to complete OAuth flow")
    else:
        configs.extend([
            "BLOGGER_CLIENT_ID=",
            "BLOGGER_CLIENT_SECRET=",
            "BLOGGER_BLOG_ID="
        ])
    
    # Ghost
    ghost_url = input("Enter Ghost blog URL (or press Enter to skip): ").strip()
    if ghost_url:
        ghost_key = input("Enter Ghost admin API key: ").strip()
        configs.extend([
            f"GHOST_API_URL={ghost_url}",
            f"GHOST_ADMIN_API_KEY={ghost_key}"
        ])
    else:
        configs.extend([
            "GHOST_API_URL=",
            "GHOST_ADMIN_API_KEY="
        ])
    
    # Write configuration
    with open(env_file, 'w') as f:
        f.write("# Solana Bot Tournament - Environment Configuration\n")
        f.write("# Generated by setup_env.py\n\n")
        for config in configs:
            f.write(f"{config}\n")
    
    print(f"\n[OK] Configuration saved to {env_file}")
    print("\nNext steps:")
    print("1. Run: pip install -e .")
    print("2. Test: python -m solana_bot_tournament.cli daily")
    print("3. Dashboard: python -m solana_bot_tournament.cli dashboard")
    
    return True


def validate_environment():
    """Validate current environment configuration."""
    print("Validating environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("[ERROR] .env file not found. Run setup first.")
        return False
    
    # Load environment variables
    env_vars = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Check required variables
    issues = []
    
    helius_key = env_vars.get('HELIUS_API_KEY', '')
    if not helius_key or helius_key.startswith('your_'):
        issues.append("[WARNING] HELIUS_API_KEY not configured (required for real data)")
    else:
        print("[OK] Helius API key configured")
    
    # Check optional but related variables
    tg_token = env_vars.get('TELEGRAM_BOT_TOKEN', '')
    tg_chat = env_vars.get('TELEGRAM_CHAT_ID', '')
    if tg_token and not tg_chat:
        issues.append("[WARNING] Telegram token provided but chat ID missing")
    elif tg_token and tg_chat:
        print("[OK] Telegram alerts configured")
    
    twitter_keys = [
        env_vars.get('TWITTER_API_KEY', ''),
        env_vars.get('TWITTER_API_SECRET', ''),
        env_vars.get('TWITTER_ACCESS_TOKEN', ''),
        env_vars.get('TWITTER_ACCESS_SECRET', '')
    ]
    if any(twitter_keys) and not all(twitter_keys):
        issues.append("[WARNING] Incomplete Twitter configuration (need all 4 keys)")
    elif all(twitter_keys):
        print("[OK] Twitter posting configured")
    
    # Check wallet addresses
    wallet_vars = ['TROJAN_WALLET_ADDRESS', 'TRADEWIZ_WALLET_ADDRESS', 'FROGBOT_WALLET_ADDRESS']
    configured_wallets = []
    missing_wallets = []
    
    for wallet_var in wallet_vars:
        wallet_addr = env_vars.get(wallet_var, '')
        bot_name = wallet_var.replace('_WALLET_ADDRESS', '')
        
        if not wallet_addr or wallet_addr.startswith('your_'):
            missing_wallets.append(bot_name)
        elif validate_solana_address(wallet_addr):
            configured_wallets.append(bot_name)
        else:
            issues.append(f"[WARNING] Invalid Solana address format for {bot_name}: {wallet_addr[:10]}...")
    
    if configured_wallets:
        print(f"[OK] Configured wallet addresses: {', '.join(configured_wallets)}")
    
    if missing_wallets:
        issues.append(f"[WARNING] Missing wallet addresses for: {', '.join(missing_wallets)}")
    
    # Check blog platform configurations
    blog_platforms = {
        'Medium': env_vars.get('MEDIUM_ACCESS_TOKEN', ''),
        'Dev.to': env_vars.get('DEVTO_API_KEY', ''),
        'Hashnode': env_vars.get('HASHNODE_ACCESS_TOKEN', ''),
        'Blogger': env_vars.get('BLOGGER_CLIENT_ID', '') and env_vars.get('BLOGGER_CLIENT_SECRET', ''),
        'Ghost': env_vars.get('GHOST_API_URL', '')
    }
    
    configured_blogs = [platform for platform, key in blog_platforms.items() 
                       if key and not key.startswith('your_')]
    
    if configured_blogs:
        print(f"[OK] Blog publishing configured for: {', '.join(configured_blogs)}")
    else:
        print("[INFO] No blog platforms configured (reports will only be saved locally)")
    
    # Check for incomplete blog configurations
    if env_vars.get('HASHNODE_ACCESS_TOKEN', '') and not env_vars.get('HASHNODE_PUBLICATION_ID', ''):
        issues.append("[WARNING] Hashnode token provided but publication ID missing")
    
    if env_vars.get('BLOGGER_CLIENT_ID', '') and not env_vars.get('BLOGGER_CLIENT_SECRET', ''):
        issues.append("[WARNING] Blogger Client ID provided but Client Secret missing")
    
    if env_vars.get('BLOGGER_CLIENT_ID', '') and not env_vars.get('BLOGGER_BLOG_ID', ''):
        issues.append("[WARNING] Blogger Client ID provided but Blog ID missing")
    
    if env_vars.get('GHOST_API_URL', '') and not env_vars.get('GHOST_ADMIN_API_KEY', ''):
        issues.append("[WARNING] Ghost URL provided but admin API key missing")
    
    if issues:
        print("\n[WARNING] Configuration issues found:")
        for issue in issues:
            print(f"   {issue}")
        return False
    
    print("\n[OK] Environment configuration looks good!")
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        validate_environment()
    else:
        setup_environment()