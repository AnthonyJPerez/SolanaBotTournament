import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from solana_bot_tournament.jobs import (
    fetch_bot_trades, parse_transactions_to_trades, calculate_pnl_from_transaction,
    extract_symbol_from_transaction, trade_to_dict, generate_daily_report,
    generate_weekly_report
)
from solana_bot_tournament.models import Trade


def test_fetch_bot_trades_empty_address():
    trades = fetch_bot_trades("", "TestBot")
    assert trades == []


def test_fetch_bot_trades_placeholder_address():
    trades = fetch_bot_trades("<PLACEHOLDER_ADDRESS>", "TestBot")
    assert trades == []


def test_parse_transactions_to_trades():
    mock_transactions = {
        "transactions": [
            {
                "timestamp": 1234567890,
                "memo": "snipe buy BONK",
                # Add other transaction fields as needed
            }
        ]
    }
    
    with patch('solana_bot_tournament.jobs.calculate_pnl_from_transaction', return_value=0.1), \
         patch('solana_bot_tournament.jobs.extract_symbol_from_transaction', return_value="BONK"):
        
        trades = parse_transactions_to_trades(mock_transactions, "TestBot")
        assert len(trades) == 1
        assert trades[0].pnl == 0.1
        assert trades[0].symbol == "BONK"
        assert trades[0].strategy == "sniper"


def test_calculate_pnl_from_transaction():
    mock_tx = {"some": "data"}
    pnl = calculate_pnl_from_transaction(mock_tx)
    assert pnl == 0.0  # Mock implementation returns 0


def test_extract_symbol_from_transaction():
    mock_tx = {"some": "data"}
    symbol = extract_symbol_from_transaction(mock_tx)
    assert symbol == "UNKNOWN"  # Mock implementation returns UNKNOWN


def test_trade_to_dict():
    trade = Trade(
        pnl=0.1,
        symbol="BONK",
        ts=1234567890,
        trigger="test",
        strategy="sniper",
        bot="TestBot"
    )
    
    result = trade_to_dict(trade)
    expected = {
        'pnl': 0.1,
        'symbol': "BONK",
        'ts': 1234567890,
        'trigger': "test",
        'strategy': "sniper",
        'bot': "TestBot"
    }
    assert result == expected


def test_trade_to_dict_no_bot_attribute():
    trade = Trade(0.1, "BONK", 1234567890, "test", "sniper")
    # Remove bot attribute to test fallback
    if hasattr(trade, 'bot'):
        delattr(trade, 'bot')
    
    result = trade_to_dict(trade)
    assert result['bot'] == 'unknown'


@patch('solana_bot_tournament.jobs.BLOG_DIR', Path('/tmp/test_blog'))
@patch('builtins.open', create=True)
def test_generate_daily_report(mock_open):
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    
    metrics = {"TestBot": {"win_rate": 75.0, "avg_pnl": 0.05}}
    balance_history = {"1": {"TestBot": 50.5}}
    
    generate_daily_report(1, metrics, balance_history)
    
    mock_open.assert_called_once()
    mock_file.write.assert_called_once()


@patch('solana_bot_tournament.jobs.BLOG_DIR', Path('/tmp/test_blog'))
@patch('builtins.open', create=True)
def test_generate_weekly_report(mock_open):
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    
    metrics = {"TestBot": {"win_rate": 70.0, "avg_pnl": 0.03}}
    balance_history = {"7": {"TestBot": 51.0}}
    
    generate_weekly_report(7, metrics, balance_history)
    
    mock_open.assert_called_once()
    mock_file.write.assert_called_once()