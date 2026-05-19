"""
Auction Market Theory (AMT) — Auction Phases & Exploration
"""
import numpy as np
import pandas as pd

class AuctionMarketDetector:
    """Detects auction phases: open exploration, range formation, trend, value area."""

    def analyze(self, df):
        if len(df) < 30:
            return []
        recent = df.tail(30)
        close = recent["Close"].iloc[-1]
        high = recent["High"].max()
        low = recent["Low"].min()
        range_pct = (high - low) / low * 100

        # Split into halves to see exploration
        first_half = recent.iloc[:15]
        second_half = recent.iloc[15:]
        fh_range = first_half["High"].max() - first_half["Low"].min()
        sh_range = second_half["High"].max() - second_half["Low"].min()

        signals = []

        # Trend phase: expanding range, one-direction
        if range_pct > 4 and fh_range < sh_range * 0.6:
            dir = "LONG" if close > first_half["Close"].mean() else "SHORT"
            signals.append({
                "type": "AMT_TREND",
                "direction": dir,
                "confidence": 60,
                "detail": f"Auction trend phase: range={range_pct:.1f}% expanding"
            })

        # Range formation: contracting range
        if fh_range > sh_range * 1.5:
            signals.append({
                "type": "AMT_RANGE_FORMATION",
                "direction": "NEUTRAL",
                "confidence": 50,
                "detail": f"Auction range formation: {fh_range:.4f} -> {sh_range:.4f}"
            })

        # Value area estimation: prices clustered around mean
        mean_price = recent["Close"].mean()
        std_price = recent["Close"].std()
        if std_price / mean_price < 0.02:
            signals.append({
                "type": "AMT_VALUE_AREA",
                "direction": "NEUTRAL",
                "confidence": 45,
                "detail": f"Value area: {mean_price:.2f} ± {std_price:.4f}"
            })

        return signals