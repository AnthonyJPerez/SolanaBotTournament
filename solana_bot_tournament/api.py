"""External HTTP wrappers (Helius, Telegram, Twitter, etc.)."""
from __future__ import annotations
import requests
import tweepy
import logging
from typing import Optional, Dict, Any
from .config import HELIUS_API_KEY, TG_TOKEN, TG_CHAT_ID, TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

_session = requests.Session(); _session.headers.update({"Content-Type":"application/json"})
_session.mount("https://", requests.adapters.HTTPAdapter(max_retries=3))
BASE_URL = "https://api.helius.xyz/v0"

def helius_get(path: str, **params) -> Dict[str, Any]:
    """Fetch data from Helius API with proper error handling."""
    if not HELIUS_API_KEY:
        raise ValueError("HELIUS_API_KEY not configured")
    
    params["api-key"] = HELIUS_API_KEY
    
    try:
        response = _session.get(f"{BASE_URL}{path}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logging.error(f"Timeout when calling Helius API: {path}")
        raise
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Helius API {path}: {e}")
        raise
    except ValueError as e:
        logging.error(f"Invalid JSON response from Helius API {path}: {e}")
        raise

# social
TW_API = None
if TWITTER_API_KEY:
    _TW_AUTH = tweepy.OAuth1UserHandler(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    TW_API   = tweepy.API(_TW_AUTH)

def telegram_send(msg: str) -> bool:
    """Send message via Telegram with error handling."""
    if not TG_TOKEN or not TG_CHAT_ID:
        logging.warning("Telegram credentials not configured")
        return False
    
    try:
        response = _session.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            json={"chat_id": TG_CHAT_ID, "text": msg},
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False

def twitter_send(msg: str, path: Optional[str] = None) -> bool:
    """Send tweet with optional media attachment."""
    if not TWITTER_API_KEY or not TW_API:
        logging.warning("Twitter API not configured")
        return False
    
    try:
        if path:
            TW_API.update_status_with_media(msg, str(path))
        else:
            TW_API.update_status(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to send tweet: {e}")
        return False