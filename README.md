# Solana Bot Tournament

Automates three Solana DEX trading bots (Trojan, TradeWiz, FrogBot) in a friendly “bot‑war,”
tracks performance, raises alerts, publishes daily/weekly markdown reports, tweets
summaries, and serves an interactive Streamlit dashboard.

## Quick Start
```bash
# 1. create & activate venv (Unix/macOS)  
python -m venv .venv
source .venv/bin/activate
# on Windows: .venv\Scripts\activate

# 2. install package
pip install -e .  # editable install

# 3. configure environment variables
python setup_env.py  # interactive setup
# OR manually copy .env.example to .env and edit

# 4. run a daily cycle
solana-bot daily

# 5. launch dashboard
streamlit run -m solana_bot_tournament.dashboard
```

### Environment Variables
| Var | Purpose |
|-----|---------|
| `HELIUS_API_KEY` | Access to Helius Enhanced Tx API ([helius.dev](https://www.helius.dev/docs/enhanced-transactions?utm_source=chatgpt.com)) |
| `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` | Optional Telegram alerts ([core.telegram.org](https://core.telegram.org/bots/api?utm_source=chatgpt.com)) |
| `TWITTER_*` | Tweepy posting creds ([docs.tweepy.org](https://docs.tweepy.org/en/stable/api.html?utm_source=chatgpt.com)) |

### Project Layout
```text
solana_bot_tournament/
  __init__.py        # package globals
  config.py          # constants & env helpers
  api.py             # Helius + social wrappers
  models.py          # dataclasses for Trades & Metrics
  analytics.py       # compute_metrics, Sharpe, etc.
  persistence.py     # JSON read/write helpers
  alerting.py        # Telegram/Twitter helpers
  charts.py          # matplotlib utils
  templates.py       # Jinja strings
  dashboard.py       # Streamlit app
  cli.py             # argparse entry‑point
blog_posts/          # generated content
tests/               # pytest suite
pyproject.md
README.md
```

## Packaging & Installation
Uses **PEP 621** `pyproject.md`; no `setup.py` needed  ([packaging.python.org](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/?utm_source=chatgpt.com)). Editable install lets you hack code and rerun instantly.

## Testing
```bash
pytest -q
```
`pytest` auto‑discovers tests in the *tests/* directory following best practices ([docs.pytest.org](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html?utm_source=chatgpt.com)).

---