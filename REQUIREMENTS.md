# Solana Bot Tournament — Feature Requirements

> **Scope**: This document enumerates **all functional and non‑functional requirements** for the Solana Bot Tournament project.  It acts as the single source of truth for implementation, QA, onboarding, and future roadmap planning.

---

## 1 · Functional Requirements

|  ID    |  Category          |  Requirement                                                                                                                                                                 |
| ------ | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  F‑01  |  Onboarding        |  The system SHALL create or import **three isolated Solana wallets** (Trojan, TradeWiz, FrogBot) and fund each with an equal, configurable amount of SOL.                    |
|  F‑02  |  Bot Integration   |  The system SHALL programmatically interact with each bot’s public interface (Telegram or API) to enable **fully automated trading**.                                        |
|  F‑03  |  Trade Ingestion   |  The system SHALL retrieve **enhanced transaction data** for every wallet via the Helius Enhanced Transactions API at least once per hour (configurable).                    |
|  F‑04  |  PnL Computation   |  The system SHALL compute per‑trade PnL (lamports → SOL), win/loss, running cumulative PnL, and drawdown.                                                                    |
|  F‑05  |  Strategy Tagging  |  The system SHALL classify each trade into one of { `sniper`, `copy_trade`, `auto`, `manual`, `unknown` } by inspecting transaction memos and metadata.                      |
|  F‑06  |  Daily Metrics     |  The system SHALL calculate daily metrics per bot: **balance**, **win rate**, **average PnL**, **max drawdown**, **strategy mix** and store them in `balance_history.json`.  |
|  F‑07  |  Notifications     |  The system SHALL send a **Telegram alert** if *Win Rate < WIN\_RATE\_MIN* **or** *Max DD < MAX\_DRAWDOWN\_LIMIT* for any bot on a given day.                                |
|  F‑08  |  Blog Generation   |  The system SHALL render a **Markdown** daily report and weekly summary via Jinja2 templates and save them under `blog_posts/`.                                              |
|  F‑09  |  Twitter Posting   |  The system SHALL tweet daily & weekly highlights, optionally with a performance chart image, via the Tweepy API.                                                            |
|  F‑10  |  Dashboard         |  The system SHALL expose a **Streamlit dashboard** offering: (a) balance chart, (b) full trade log, (c) strategy distribution bar chart, selectable per bot.                 |
|  F‑11  |  CLI               |  A single command‑line tool `solana‑bot` SHALL support the modes `daily`, `weekly`, and `dashboard`.                                                                         |
|  F‑12  |  Packaging         |  The project SHALL be installable via `pip install .` or `pip install -e .` using a `pyproject.md` that declares all Python dependencies.                                  |
|  F‑13  |  Unit Tests        |  The project SHALL include pytest tests covering ≥ 80 % of analytics, alerting, and tagging logic.                                                                           |
|  F‑14  |  Extensibility     |  The architecture SHALL allow adding new bots or strategies with only configuration changes, not core‑code edits.                                                            |

## 2 · Non‑Functional Requirements

### 2.1 Performance

* **N‑01** The daily job SHALL finish in < 2 minutes on a consumer laptop with 50 Mbps Internet.
* **N‑02** The Streamlit dashboard SHALL load its initial view in ≤ 3 seconds with up to 5,000 stored trades.

### 2.2 Reliability & Resilience

* **N‑03** HTTP requests to Helius SHALL be retried ≥ 3 times on transient failures.
* **N‑04** The system SHALL not lose historical data; history and trade logs are persisted to JSON files in project root.

### 2.3 Security

* **N‑05** Private keys SHALL **never** be stored in plaintext; only public wallet addresses are handled by the automation.
* **N‑06** Environment variables SHALL be used for all API keys and secrets.

### 2.4 Maintainability

* **N‑07** Code SHALL follow PEP 8 style guidelines and be fully type‑annotated (≥ 90 %).
* **N‑08** Modules SHALL be split by concern (`api`, `analytics`, `alerting`, etc.) to ensure testability and reusability.

### 2.5 Portability

* **N‑09** The project SHALL run on macOS, Linux, and Windows (via WSL) with Python 3.10 +.

## 3 · Installation & Setup Requirements

1. **Python 3.10+** installed on the system.
2. **Virtual‑environment** usage is mandatory to avoid dependency clashes.  Example:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e .
   ```
3. A `.env` or shell export providing:

   * `HELIUS_API_KEY`
   * `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (optional)
   * `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET` (optional)
4. Run \`\` to initialise history and generate Day‑1 posts.

## 4 · Deployment & Operations

* **D‑01** For local use, a simple cron or Windows Task Scheduler entry SHALL invoke `solana‑bot daily` once every 24 h.
* **D‑02** For cloud/GitHub Actions deployment, a sample workflow file SHALL be provided (future work).

## 5 · Testing & QA

* **T‑01** Automated pytest suite MUST pass with `pytest -q` and achieve ≥ 80 % coverage.
* **T‑02** Manual test checklist SHALL verify dashboard rendering, Telegram alert delivery, and blog markdown accuracy.

## 6 · Future / Stretch Goals

* **S‑01** Add a Flask REST API for programmatic queries.
* **S‑02** Add CI/CD pipeline (GitHub Actions) to publish blog posts to a static site host.
* **S‑03** Integrate additional bots or chains (e.g., Ethereum snipers) under the same analytics framework.

---

> **Document Owner:** *Project Lead* **Last Updated:** {{DATE}}
