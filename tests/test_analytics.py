import pytest
from solana_bot_tournament.analytics import compute_metrics, classify_strategy
from solana_bot_tournament.models import Trade


def test_classify_strategy():
    assert classify_strategy("snipe buy") == "sniper"
    assert classify_strategy("SNIPER attack") == "sniper"
    assert classify_strategy("copy from 0x123") == "copy_trade"
    assert classify_strategy("COPY TRADE") == "copy_trade"
    assert classify_strategy("auto trade") == "auto"
    assert classify_strategy("AUTO mode") == "auto"
    assert classify_strategy("manual entry") == "manual"
    assert classify_strategy("") == "unknown"
    assert classify_strategy(None) == "unknown"
    assert classify_strategy("random text") == "manual"


def test_compute_metrics():
    trades = [Trade(0.1, "AAA", 1, None, "sniper"), Trade(-0.05, "BBB", 2, None, "copy_trade")]
    m = compute_metrics(trades)
    assert m["win_rate"] == 50.0
    assert m["avg_pnl"] == pytest.approx(0.025)
    assert m["max_dd"] == pytest.approx(-0.05)


def test_compute_metrics_empty():
    m = compute_metrics([])
    assert m["win_rate"] == 0.0
    assert m["avg_pnl"] == 0.0
    assert m["max_dd"] == 0.0


def test_compute_metrics_all_wins():
    trades = [Trade(0.1, "A", 1, None, "sniper"), Trade(0.05, "B", 2, None, "auto")]
    m = compute_metrics(trades)
    assert m["win_rate"] == 100.0
    assert m["avg_pnl"] == pytest.approx(0.075)
    assert m["max_dd"] == 0.0


def test_compute_metrics_all_losses():
    trades = [Trade(-0.1, "A", 1, None, "sniper"), Trade(-0.05, "B", 2, None, "auto")]
    m = compute_metrics(trades)
    assert m["win_rate"] == 0.0
    assert m["avg_pnl"] == pytest.approx(-0.075)
    assert m["max_dd"] == pytest.approx(-0.15)


def test_compute_metrics_drawdown_calculation():
    # Test cumulative drawdown calculation
    trades = [
        Trade(0.1, "A", 1, None, "sniper"),    # cum: 0.1, peak: 0.1, dd: 0
        Trade(-0.2, "B", 2, None, "auto"),     # cum: -0.1, peak: 0.1, dd: -0.2
        Trade(0.05, "C", 3, None, "manual"),   # cum: -0.05, peak: 0.1, dd: -0.15
        Trade(0.3, "D", 4, None, "sniper"),    # cum: 0.25, peak: 0.25, dd: 0
    ]
    m = compute_metrics(trades)
    assert m["max_dd"] == pytest.approx(-0.2)