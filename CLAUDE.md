# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Installation & Setup
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate          # Unix/macOS
# .venv\Scripts\activate           # Windows

# Install in editable mode
pip install -e .
```

### Running the Application
```bash
# Run daily tournament cycle
solana-bot daily

# Run weekly tournament cycle  
solana-bot weekly [--day N]

# Launch Streamlit dashboard
solana-bot dashboard
# or alternatively:
streamlit run -m solana_bot_tournament.dashboard
```

### Testing
```bash
# Run all tests
pytest -q

# Run specific test module
pytest tests/test_analytics.py -v
pytest tests/test_alerting.py -v
```

## Architecture Overview

This is a **Solana trading bot tournament system** that tracks and compares the performance of three trading bots: Trojan, TradeWiz, and FrogBot. The system fetches transaction data via Helius API, analyzes performance metrics, generates reports, and provides both alerting and dashboard capabilities.

### Core Architecture

**Data Flow**: Helius API → Trade Analysis → Metrics Computation → Reports/Alerts/Dashboard

**Key Components**:
- `api.py`: External API wrappers (Helius, Telegram, Twitter)
- `models.py`: Core data structures (`Trade` dataclass)
- `analytics.py`: Performance metrics calculation (win rate, avg PnL, max drawdown)
- `persistence.py`: JSON-based data storage
- `alerting.py`: Notification systems (Telegram/Twitter)
- `dashboard.py`: Streamlit web interface
- `cli.py`: Command-line entry point

### Bot Identification & Strategy Classification

The system classifies trading strategies by analyzing transaction memos:
- **copy_trade**: Contains "COPY"  
- **sniper**: Contains "SNIPE" or "SNIPER"
- **auto**: Contains "AUTO"
- **manual**: Default fallback

### Required Environment Variables

Set these environment variables for full functionality:
- `HELIUS_API_KEY`: Helius Enhanced Transactions API access
- `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`: Optional Telegram alerts
- `TWITTER_*`: Twitter API credentials for posting (via tweepy)

### Package Structure

Uses **PEP 621** `pyproject.md` configuration. The CLI entry point `solana-bot` is defined in `project.scripts` and maps to `solana_bot_tournament.cli:main`.

**Note**: The `jobs` module referenced in `cli.py` (job_daily, job_weekly functions) is not yet implemented in the codebase.