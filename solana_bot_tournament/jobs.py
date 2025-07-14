"""Daily and weekly job orchestration for the Solana bot tournament."""
from __future__ import annotations
import datetime as dt
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from .config import (
    WALLETS, BLOG_DIR, HISTORY_FILE, TRADE_LOG_FILE, START_DATE,
    INITIAL_BALANCE_SOL, WIN_RATE_MIN, MAX_DRAWDOWN_LIMIT
)
import requests
from .api import helius_get
from .models import Trade
from .analytics import compute_metrics, classify_strategy
from .persistence import load_json, save_json
from .alerting import alert_low_win, alert_drawdown, tweet_daily, tweet_weekly
from .charts import balance_chart
from .templates import DAILY, WEEKLY
from .blog_publisher import publish_blog_post


def job_daily() -> bool:
    """Execute daily tournament cycle: fetch trades, compute metrics, generate reports."""
    today = dt.date.today()
    day_number = (today - START_DATE).days + 1
    
    print(f"Running daily job for Day {day_number} ({today})")
    
    # Load existing data
    trade_log = load_json(TRADE_LOG_FILE, [])
    balance_history = load_json(HISTORY_FILE, {})
    
    # Fetch new trades for each bot
    new_trades = []
    bot_metrics = {}
    
    for bot_name, wallet_address in WALLETS.items():
        print(f"Processing {bot_name}...")
        
        # Fetch enhanced transactions (mock implementation - replace with real Helius API call)
        bot_trades = fetch_bot_trades(wallet_address, bot_name)
        new_trades.extend(bot_trades)
        
        # Compute metrics for this bot - with validation
        try:
            bot_trade_dicts = [t for t in trade_log if t.get('bot') == bot_name]
            validated_trades = []
            
            for trade_dict in bot_trade_dicts:
                try:
                    validated_trades.append(Trade(**trade_dict))
                except (TypeError, ValueError) as e:
                    logging.warning(f"Skipping invalid trade data: {e}")
                    continue
            
            all_bot_trades = validated_trades + bot_trades
            metrics = compute_metrics(all_bot_trades)
        except Exception as e:
            logging.error(f"Error computing metrics for {bot_name}: {e}")
            metrics = {"win_rate": 0.0, "avg_pnl": 0.0, "max_dd": 0.0}
        bot_metrics[bot_name] = metrics
        
        # Check for alerts
        if metrics['win_rate'] < WIN_RATE_MIN:
            alert_low_win(bot_name, metrics['win_rate'], day_number)
        
        if metrics['max_dd'] < MAX_DRAWDOWN_LIMIT:
            alert_drawdown(bot_name, metrics['max_dd'], day_number)
    
    # Update trade log with error handling
    try:
        new_trade_dicts = [trade_to_dict(t) for t in new_trades]
        trade_log.extend(new_trade_dicts)
        
        if not save_json(TRADE_LOG_FILE, trade_log):
            logging.error("Failed to save trade log")
            return False
    except Exception as e:
        logging.error(f"Error updating trade log: {e}")
        return False
    
    # Update balance history with error handling
    try:
        day_key = str(day_number)
        daily_balances = {}
        
        for bot in WALLETS.keys():
            bot_pnl = 0.0
            for trade_dict in trade_log:
                if trade_dict.get('bot') == bot:
                    bot_pnl += trade_dict.get('pnl', 0.0)
            
            daily_balances[bot] = INITIAL_BALANCE_SOL + bot_pnl
        
        balance_history[day_key] = daily_balances
        
        if not save_json(HISTORY_FILE, balance_history):
            logging.error("Failed to save balance history")
            return False
    except Exception as e:
        logging.error(f"Error updating balance history: {e}")
        return False
    
    # Generate daily report
    report_content = generate_daily_report(day_number, bot_metrics, balance_history)
    
    # Create and tweet chart with error handling
    try:
        chart_path = BLOG_DIR / f"day_{day_number}_chart.png"
        
        if balance_chart(balance_history, chart_path):
            tweet_message = f"Day {day_number} Results! 🤖 Check out the bot tournament standings"
            if not tweet_daily(tweet_message, chart_path):
                logging.warning("Failed to send daily tweet")
        else:
            logging.error("Failed to generate daily chart")
    except Exception as e:
        logging.error(f"Error generating chart or tweet: {e}")
    
    # Publish to blogs
    try:
        blog_title = f"Day {day_number} - Solana Bot Tournament Results"
        blog_tags = ["solana", "trading", "bots", "cryptocurrency", "defi", "tournament"]
        
        blog_results = publish_blog_post(blog_title, report_content, blog_tags)
        
        if blog_results:
            successful_publications = [platform for platform, result in blog_results.items() 
                                     if result.get("success")]
            if successful_publications:
                logging.info(f"Published to blogs: {', '.join(successful_publications)}")
            else:
                logging.warning("Failed to publish to any blog platforms")
        else:
            logging.info("No blog platforms configured for publishing")
            
    except Exception as e:
        logging.error(f"Error publishing to blogs: {e}")
    
    print(f"Daily job completed for Day {day_number}")
    return True


def job_weekly(end_day: Optional[int] = None) -> bool:
    """Execute weekly tournament summary."""
    if end_day is None:
        end_day = (dt.date.today() - START_DATE).days + 1
    
    print(f"Running weekly job ending on Day {end_day}")
    
    # Load data
    trade_log = load_json(TRADE_LOG_FILE, [])
    balance_history = load_json(HISTORY_FILE, {})
    
    # Calculate weekly metrics
    week_start = max(1, end_day - 6)
    weekly_trades = [Trade(**t) for t in trade_log 
                    if week_start <= t.get('day', 1) <= end_day]
    
    bot_weekly_metrics = {}
    for bot_name in WALLETS.keys():
        bot_trades = [t for t in weekly_trades if t.bot == bot_name]
        bot_weekly_metrics[bot_name] = compute_metrics(bot_trades)
    
    # Generate weekly report
    report_content = generate_weekly_report(end_day, bot_weekly_metrics, balance_history)
    
    # Create and tweet weekly chart
    chart_path = BLOG_DIR / f"week_ending_day_{end_day}_chart.png"
    balance_chart(balance_history, chart_path)
    
    tweet_message = f"Week {end_day//7 + 1} Summary! 📊 Bot tournament weekly recap"
    tweet_weekly(tweet_message, chart_path)
    
    # Publish weekly summary to blogs
    try:
        week_num = end_day // 7 + 1
        blog_title = f"Week {week_num} - Solana Bot Tournament Weekly Summary"
        blog_tags = ["solana", "trading", "bots", "cryptocurrency", "defi", "weekly-summary"]
        
        blog_results = publish_blog_post(blog_title, report_content, blog_tags)
        
        if blog_results:
            successful_publications = [platform for platform, result in blog_results.items() 
                                     if result.get("success")]
            if successful_publications:
                logging.info(f"Published weekly summary to blogs: {', '.join(successful_publications)}")
            else:
                logging.warning("Failed to publish weekly summary to any blog platforms")
        else:
            logging.info("No blog platforms configured for weekly publishing")
            
    except Exception as e:
        logging.error(f"Error publishing weekly summary to blogs: {e}")
    
    print(f"Weekly job completed ending on Day {end_day}")
    return True


def fetch_bot_trades(wallet_address: str, bot_name: str) -> List[Trade]:
    """Fetch enhanced transaction data for a bot wallet."""
    # Mock implementation - in real usage, this would call Helius Enhanced Transactions API
    # For now, return empty list to avoid API dependency
    
    if not wallet_address or wallet_address.startswith("<"):
        print(f"Skipping {bot_name} - wallet address not configured")
        return []
    
    try:
        # Example Helius API call (commented out to avoid real API dependency)
        # transactions = helius_get("/transactions", addresses=[wallet_address])
        # return parse_transactions_to_trades(transactions, bot_name)
        
        print(f"Mock: Fetched 0 new trades for {bot_name}")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error fetching trades for {bot_name}: {e}")
        return []
    except Exception as e:
        logging.error(f"Unexpected error fetching trades for {bot_name}: {e}")
        return []


def parse_transactions_to_trades(transactions: dict, bot_name: str) -> List[Trade]:
    """Parse Helius transaction data into Trade objects."""
    trades = []
    
    for tx in transactions.get('transactions', []):
        # Extract PnL, symbol, timestamp, etc. from transaction
        # This is a simplified example
        pnl = calculate_pnl_from_transaction(tx)
        symbol = extract_symbol_from_transaction(tx)
        timestamp = tx.get('timestamp', 0)
        memo = tx.get('memo', '')
        strategy = classify_strategy(memo)
        
        if pnl != 0:  # Only include trades with actual PnL
            trades.append(Trade(
                pnl=pnl,
                symbol=symbol,
                ts=timestamp,
                trigger=memo,
                strategy=strategy
            ))
    
    return trades


def calculate_pnl_from_transaction(tx: dict) -> float:
    """Calculate PnL from a transaction."""
    # Mock implementation - real version would analyze token transfers
    return 0.0


def extract_symbol_from_transaction(tx: dict) -> str:
    """Extract token symbol from transaction."""
    # Mock implementation - real version would look at token metadata
    return "UNKNOWN"


def generate_daily_report(day: int, metrics: Dict, balance_history: Dict) -> str:
    """Generate daily markdown report and return content."""
    report_content = DAILY.render(
        day=day,
        metrics=metrics,
        balances=balance_history.get(str(day), {})
    )
    
    report_path = BLOG_DIR / f"day_{day}_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Generated daily report: {report_path}")
    return report_content


def generate_weekly_report(end_day: int, metrics: Dict, balance_history: Dict) -> str:
    """Generate weekly markdown summary and return content."""
    week_num = end_day // 7 + 1
    report_content = WEEKLY.render(
        wk=week_num,
        end_day=end_day,
        metrics=metrics,
        balance_history=balance_history
    )
    
    report_path = BLOG_DIR / f"week_{week_num}_summary.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"Generated weekly report: {report_path}")
    return report_content


def trade_to_dict(trade: Trade) -> dict:
    """Convert Trade object to dictionary for JSON serialization."""
    return {
        'pnl': trade.pnl,
        'symbol': trade.symbol,
        'ts': trade.ts,
        'trigger': trade.trigger,
        'strategy': trade.strategy,
        'bot': getattr(trade, 'bot', 'unknown')
    }