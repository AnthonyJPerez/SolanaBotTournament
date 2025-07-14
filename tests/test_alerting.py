from unittest.mock import patch
from pathlib import Path
from solana_bot_tournament import alerting


@patch("solana_bot_tournament.alerting.telegram_send")
def test_alert_low_win(mock_send):
    alerting.alert_low_win("Trojan", 40.0, 3)
    mock_send.assert_called_once_with("⚠️ Trojan win rate is low (40.0%) on Day 3")


@patch("solana_bot_tournament.alerting.telegram_send")
def test_alert_drawdown(mock_send):
    alerting.alert_drawdown("TradeWiz", -2.5, 5)
    mock_send.assert_called_once_with("⚠️ TradeWiz drawdown -2.5 SOL on Day 5")


@patch("solana_bot_tournament.alerting.twitter_send")
def test_tweet_daily(mock_send):
    chart_path = Path("/tmp/test_chart.png")
    alerting.tweet_daily("Daily update!", chart_path)
    mock_send.assert_called_once_with("Daily update!", chart_path)


@patch("solana_bot_tournament.alerting.twitter_send")
def test_tweet_weekly(mock_send):
    chart_path = Path("/tmp/weekly_chart.png")
    alerting.tweet_weekly("Weekly summary!", chart_path)
    mock_send.assert_called_once_with("Weekly summary!", chart_path)