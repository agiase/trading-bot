"""
Level 2 / Orderbook — Imbalance, Wall Detection (estimated from OHLCV)
"""
import numpy as np
import pandas as pd

class Level2Detector:
    """Estimates orderbook-level signals from OHLCV + volume."""

    def analyze(self, df):
        if len(df) < 20:
            return []
        recent = df.tail(20)
        signals = []

        # Imbalance proxy: compare volume on up vs down bars
        up_vol = recent[recent["Close"] > recent["Open"]]["Volume"].sum()
        down_vol = recent[recent["Close"] < recent["Open"]]["Volume"].sum()
        total = up_vol + down_vol
        if total == 0:
            return []

        imbalance = (up_vol - down_vol) / total
        if imbalance > 0.3:
            signals.append({
                "type": "L2_BUY_IMBALANCE",
                "direction": "LONG",
                "confidence": min(50 + int(imbalance * 40), 75),
                "detail": f"Buy imbalance={imbalance:.2f}"
            })
        elif imbalance < -0.3:
            signals.append({
                "type": "L2_SELL_IMBALANCE",
                "direction": "SHORT",
                "confidence": min(50 + int(abs(imbalance) * 40), 75),
                "detail": f"Sell imbalance={imbalance:.2f}"
            })

        # Absorption: high volume, narrow range (consolidation near key level)
        ranges = recent["High"] - recent["Low"]
        avg_range = ranges.mean()
        avg_vol = recent["Volume"].mean()
        last = recent.iloc[-1]
        if last["Volume"] > avg_vol * 1.5 and (last["High"] - last["Low"]) < avg_range * 0.7:
            signals.append({
                "type": "L2_ABSORPTION",
                "direction": "NEUTRAL",
                "confidence": 50,
                "detail": "Orderbook absorption: high vol, narrow range"
            })

        return signals