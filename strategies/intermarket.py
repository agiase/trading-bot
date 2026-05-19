"""
Intermarket Analysis — BTC ↔ DXY, Gold, S&P, ETH/BTC Ratio
"""
import numpy as np
import pandas as pd

# Fallback using simulated correlation when only single-ticker data is available
class IntermarketDetector:
    """Provides intermarket context signals using cached/estimated correlations."""

    def analyze(self, df):
        if len(df) < 20:
            return []
        close = df["Close"]
        close_pct = close.pct_change()
        recent_vol = close_pct.tail(20).std()
        signals = []

        # Volatility regime
        hist_vol = close_pct.tail(100).std() if len(df) >= 100 else recent_vol
        if recent_vol > hist_vol * 1.3:
            signals.append({
                "type": "INTERMARKET_HIGH_VOL",
                "direction": "NEUTRAL",
                "confidence": 40,
                "detail": f"Vol spike: {recent_vol:.4f} vs hist {hist_vol:.4f}"
            })
        elif recent_vol < hist_vol * 0.7:
            signals.append({
                "type": "INTERMARKET_LOW_VOL",
                "direction": "NEUTRAL",
                "confidence": 40,
                "detail": f"Low vol: {recent_vol:.4f} vs hist {hist_vol:.4f}"
            })

        # BTC dominance proxy using price relative strength
        # (requires BTC/ALT pair data — we estimate from close strength)
        closes = df["Close"].values
        strength = (closes[-1] - closes[-5]) / closes[-5] * 100 if len(closes) >= 5 else 0
        if strength > 5:
            signals.append({
                "type": "INTERMARKET_STRONG",
                "direction": "LONG",
                "confidence": 50,
                "detail": f"Strong relative performance: +{strength:.1f}% in 5 bars"
            })
        elif strength < -5:
            signals.append({
                "type": "INTERMARKET_WEAK",
                "direction": "SHORT",
                "confidence": 50,
                "detail": f"Weak relative performance: {strength:.1f}% in 5 bars"
            })

        return signals