"""High‑level alert helpers using Telegram and Twitter wrappers."""
from __future__ import annotations
from pathlib import Path
from .api import telegram_send, twitter_send


def alert_low_win(bot: str, win_rate: float, day: int):
    telegram_send(f"⚠️ {bot} win rate is low ({win_rate}%) on Day {day}")


def alert_drawdown(bot: str, dd: float, day: int):
    telegram_send(f"⚠️ {bot} drawdown {dd} SOL on Day {day}")


def tweet_daily(message: str, chart_path: Path):
    twitter_send(message, chart_path)


def tweet_weekly(message: str, chart_path: Path):
    twitter_send(message, chart_path)