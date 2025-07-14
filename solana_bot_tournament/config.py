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

WALLETS = {
    "Trojan": "<TROJAN_WALLET_ADDRESS>",
    "TradeWiz": "<TRADEWIZ_WALLET_ADDRESS>",
    "FrogBot": "<FROGBOT_WALLET_ADDRESS>",
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