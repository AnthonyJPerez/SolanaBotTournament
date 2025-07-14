import matplotlib.pyplot as plt
import logging
from pathlib import Path
from typing import Dict, Any
from .config import WALLETS, INITIAL_BALANCE_SOL

def balance_chart(hist: Dict[str, Dict[str, float]], outfile: Path) -> bool:
    """Generate balance chart for all bots with error handling."""
    try:
        if not hist:
            logging.warning("No history data provided for chart generation")
            return False
        
        plt.figure(figsize=(10, 6))
        
        days = sorted(map(int, hist.keys()))
        if not days:
            logging.warning("No valid days found in history data")
            return False
        
        # Generate plot for each bot
        for bot in WALLETS:
            balances = []
            for day in days:
                day_data = hist.get(str(day), {})
                balance = day_data.get(bot, INITIAL_BALANCE_SOL)
                balances.append(balance)
            
            plt.plot(days, balances, label=bot, marker='o', linewidth=2)
        
        # Format chart
        plt.xlabel("Day")
        plt.ylabel("SOL Balance")
        plt.title("Bot Tournament - Balance History")
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        
        # Ensure output directory exists
        outfile.parent.mkdir(parents=True, exist_ok=True)
        
        plt.savefig(outfile, dpi=300, bbox_inches='tight')
        plt.close()
        
        logging.info(f"Chart saved to {outfile}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to generate balance chart: {e}")
        plt.close()  # Ensure plot is closed even on error
        return False
