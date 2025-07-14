import pytest
from solana_bot_tournament.templates import DAILY, WEEKLY


def test_daily_template():
    metrics = {
        "Trojan": {"win_rate": 75.0, "avg_pnl": 0.05, "max_dd": -0.1},
        "TradeWiz": {"win_rate": 65.0, "avg_pnl": 0.03, "max_dd": -0.15}
    }
    balances = {"Trojan": 52.5, "TradeWiz": 51.2}
    
    result = DAILY.render(day=5, metrics=metrics, balances=balances)
    
    assert "Day 5" in result
    assert "Trojan" in result
    assert "TradeWiz" in result
    assert "75.0%" in result
    assert "65.0%" in result
    assert "52.5" in result
    assert "51.2" in result
    assert "day_5_chart.png" in result


def test_weekly_template():
    metrics = {
        "Trojan": {"win_rate": 70.0, "avg_pnl": 0.04, "max_dd": -0.2},
        "FrogBot": {"win_rate": 80.0, "avg_pnl": 0.06, "max_dd": -0.05}
    }
    
    result = WEEKLY.render(wk=2, end_day=14, metrics=metrics)
    
    assert "Week 2" in result
    assert "Day 14" in result
    assert "Trojan" in result
    assert "FrogBot" in result
    assert "70.0%" in result
    assert "80.0%" in result
    assert "week_ending_day_14_chart.png" in result


def test_daily_template_empty_metrics():
    result = DAILY.render(day=1, metrics={}, balances={})
    
    assert "Day 1" in result
    assert "day_1_chart.png" in result


def test_weekly_template_empty_metrics():
    result = WEEKLY.render(wk=1, end_day=7, metrics={})
    
    assert "Week 1" in result
    assert "Day 7" in result
    assert "week_ending_day_7_chart.png" in result