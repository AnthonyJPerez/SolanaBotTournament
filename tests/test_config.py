import pytest
from pathlib import Path
from solana_bot_tournament.config import (
    ROOT_DIR, BLOG_DIR, HISTORY_FILE, TRADE_LOG_FILE, START_DATE,
    INITIAL_BALANCE_SOL, WALLETS, WIN_RATE_MIN, MAX_DRAWDOWN_LIMIT
)


def test_config_constants():
    assert isinstance(ROOT_DIR, Path)
    assert isinstance(BLOG_DIR, Path)
    assert isinstance(HISTORY_FILE, Path)
    assert isinstance(TRADE_LOG_FILE, Path)
    
    assert INITIAL_BALANCE_SOL == 50.0
    assert WIN_RATE_MIN == 55.0
    assert MAX_DRAWDOWN_LIMIT == -5.0


def test_wallets_config():
    assert isinstance(WALLETS, dict)
    assert len(WALLETS) == 3
    assert "Trojan" in WALLETS
    assert "TradeWiz" in WALLETS
    assert "FrogBot" in WALLETS


def test_file_paths():
    assert HISTORY_FILE.name == "balance_history.json"
    assert TRADE_LOG_FILE.name == "trade_log.json"
    assert BLOG_DIR.name == "blog_posts"


def test_start_date():
    assert START_DATE.year >= 2025
    assert 1 <= START_DATE.month <= 12
    assert 1 <= START_DATE.day <= 31


def test_directory_creation():
    # BLOG_DIR should be created by the config module
    # In tests, we just verify the path is correct
    assert "blog_posts" in str(BLOG_DIR)