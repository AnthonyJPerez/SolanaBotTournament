from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Trade:
    pnl: float
    symbol: str | None
    ts: int
    trigger: str | None
    strategy: str
    bot: str = "unknown"