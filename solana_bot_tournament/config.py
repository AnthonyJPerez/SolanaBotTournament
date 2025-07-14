from __future__ import annotations
import os
import datetime as _dt
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# Safely create blog directory
BLOG_DIR = ROOT_DIR / "blog_posts"
try:
    BLOG_DIR.mkdir(exist_ok=True, parents=True)
except OSError as e:
    logging.warning(f"Could not create blog directory {BLOG_DIR}: {e}")
    BLOG_DIR = ROOT_DIR  # Fallback to root directory
HISTORY_FILE = ROOT_DIR / "balance_history.json"
TRADE_LOG_FILE = ROOT_DIR / "trade_log.json"
START_DATE = _dt.date(2025, 7, 14)
INITIAL_BALANCE_SOL = 50.0

# Bot wallet addresses from environment variables
TROJAN_WALLET = os.getenv("TROJAN_WALLET_ADDRESS", "").strip()
TRADEWIZ_WALLET = os.getenv("TRADEWIZ_WALLET_ADDRESS", "").strip()
FROGBOT_WALLET = os.getenv("FROGBOT_WALLET_ADDRESS", "").strip()

WALLETS = {
    "Trojan": TROJAN_WALLET or "<TROJAN_WALLET_ADDRESS>",
    "TradeWiz": TRADEWIZ_WALLET or "<TRADEWIZ_WALLET_ADDRESS>", 
    "FrogBot": FROGBOT_WALLET or "<FROGBOT_WALLET_ADDRESS>",
}

WIN_RATE_MIN = 55.0
MAX_DRAWDOWN_LIMIT = -5.0

# Environment variables with validation
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY", "").strip()
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "").strip()
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "").strip()
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "").strip()
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "").strip()

# Blog publishing API keys
MEDIUM_ACCESS_TOKEN = os.getenv("MEDIUM_ACCESS_TOKEN", "").strip()
DEVTO_API_KEY = os.getenv("DEVTO_API_KEY", "").strip()
HASHNODE_ACCESS_TOKEN = os.getenv("HASHNODE_ACCESS_TOKEN", "").strip()
HASHNODE_PUBLICATION_ID = os.getenv("HASHNODE_PUBLICATION_ID", "").strip()
WORDPRESS_CLIENT_ID = os.getenv("WORDPRESS_CLIENT_ID", "").strip()
WORDPRESS_CLIENT_SECRET = os.getenv("WORDPRESS_CLIENT_SECRET", "").strip()
WORDPRESS_SITE_URL = os.getenv("WORDPRESS_SITE_URL", "").strip()
GHOST_API_URL = os.getenv("GHOST_API_URL", "").strip()
GHOST_ADMIN_API_KEY = os.getenv("GHOST_ADMIN_API_KEY", "").strip()

# Validate critical environment variables
if not HELIUS_API_KEY:
    logging.warning("HELIUS_API_KEY not set - API calls will fail")

# Validate configuration consistency
twitter_keys = [TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]
if any(twitter_keys) and not all(twitter_keys):
    logging.warning("Incomplete Twitter API configuration - some keys missing")

telegram_keys = [TG_TOKEN, TG_CHAT_ID]
if any(telegram_keys) and not all(telegram_keys):
    logging.warning("Incomplete Telegram configuration - missing token or chat ID")

# Validate wallet addresses
wallet_addresses = [TROJAN_WALLET, TRADEWIZ_WALLET, FROGBOT_WALLET]
configured_wallets = [addr for addr in wallet_addresses if addr and not addr.startswith("<")]

if not configured_wallets:
    logging.warning("No bot wallet addresses configured - only mock data will be available")
elif len(configured_wallets) < 3:
    missing_bots = []
    if not TROJAN_WALLET or TROJAN_WALLET.startswith("<"):
        missing_bots.append("Trojan")
    if not TRADEWIZ_WALLET or TRADEWIZ_WALLET.startswith("<"):
        missing_bots.append("TradeWiz")
    if not FROGBOT_WALLET or FROGBOT_WALLET.startswith("<"):
        missing_bots.append("FrogBot")
    logging.warning(f"Missing wallet addresses for: {', '.join(missing_bots)}")
else:
    logging.info(f"All {len(configured_wallets)} bot wallet addresses configured")

# Validate blog publishing configurations
blog_platforms = [
    ("Medium", MEDIUM_ACCESS_TOKEN),
    ("Dev.to", DEVTO_API_KEY),
    ("Hashnode", HASHNODE_ACCESS_TOKEN and HASHNODE_PUBLICATION_ID),
    ("WordPress", WORDPRESS_CLIENT_ID and WORDPRESS_CLIENT_SECRET and WORDPRESS_SITE_URL),
    ("Ghost", GHOST_API_URL and GHOST_ADMIN_API_KEY)
]

configured_blogs = [name for name, is_configured in blog_platforms if is_configured]
if configured_blogs:
    logging.info(f"Blog publishing configured for: {', '.join(configured_blogs)}")
else:
    logging.info("No blog platforms configured - reports will only be saved locally")