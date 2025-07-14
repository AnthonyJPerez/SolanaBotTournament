from __future__ import annotations
from collections import Counter
from typing import List, Dict, Optional
from .models import Trade


def classify_strategy(memo: Optional[str]) -> str:
    """Classify trading strategy based on transaction memo."""
    if not memo:
        return "unknown"
    
    memo_upper = memo.upper()
    if "COPY" in memo_upper:
        return "copy_trade"
    if "SNIPE" in memo_upper or "SNIPER" in memo_upper:
        return "sniper"
    if "AUTO" in memo_upper:
        return "auto"
    return "manual"


def compute_metrics(trades: List[Trade]) -> Dict[str, float]:
    """Compute trading metrics including win rate, average PnL, and max drawdown."""
    if not trades:
        return {"win_rate": 0.0, "avg_pnl": 0.0, "max_dd": 0.0}
    
    # Calculate basic metrics
    wins = sum(1 for t in trades if t.pnl > 0)
    total = len(trades)
    win_rate = round((wins / total) * 100, 2)
    avg_pnl = round(sum(t.pnl for t in trades) / total, 4)
    
    # Calculate maximum drawdown
    cumulative = 0.0
    peak = 0.0
    max_drawdown = 0.0
    
    for trade in trades:
        cumulative += trade.pnl
        peak = max(peak, cumulative)
        drawdown = cumulative - peak
        max_drawdown = min(max_drawdown, drawdown)
    
    return {
        "win_rate": win_rate,
        "avg_pnl": avg_pnl,
        "max_dd": round(max_drawdown, 4)
    }