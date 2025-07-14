"""Command‑line interface for daily/weekly jobs and dashboard."""
import argparse, sys
from .jobs import job_daily, job_weekly


def main():
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["daily", "weekly", "dashboard"], help="Run mode")
    p.add_argument("--day", type=int, help="Week ending day for weekly mode")
    args = p.parse_args()

    if args.mode == "daily":
        job_daily()
    elif args.mode == "weekly":
        job_weekly(args.day)
    elif args.mode == "dashboard":
        import streamlit.web.cli as st_cli
        sys.argv = ["streamlit", "run", "-m", "solana_bot_tournament.dashboard"]
        sys.exit(st_cli.main())