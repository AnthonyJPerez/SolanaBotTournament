import pytest
from solana_bot_tournament.models import Trade


def test_trade_creation():
    trade = Trade(
        pnl=0.1,
        symbol="BONK",
        ts=1234567890,
        trigger="snipe buy",
        strategy="sniper",
        bot="Trojan"
    )
    assert trade.pnl == 0.1
    assert trade.symbol == "BONK"
    assert trade.ts == 1234567890
    assert trade.trigger == "snipe buy"
    assert trade.strategy == "sniper"
    assert trade.bot == "Trojan"


def test_trade_default_bot():
    trade = Trade(
        pnl=-0.05,
        symbol="SOL",
        ts=1234567890,
        trigger=None,
        strategy="unknown"
    )
    assert trade.bot == "unknown"


def test_trade_none_values():
    trade = Trade(
        pnl=0.0,
        symbol=None,
        ts=0,
        trigger=None,
        strategy="manual"
    )
    assert trade.symbol is None
    assert trade.trigger is None
    assert trade.pnl == 0.0