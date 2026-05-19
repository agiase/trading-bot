"""
Liquidity Theory — Buy-side / Sell-side Liquidity Detection
"""
import numpy as np
import pandas as pd

class LiquidityDetector:
    """Detects liquidity pools and sweeps."""

    def _find_swing_highs_lows(self, df, window=10):
        highs = df["High"].values
        lows = df["Low"].values
        swing_highs = []
        swing_lows = []
        for i in range(window, len(df) - window):
            if highs[i] == max(highs[i-window:i+window+1]):
                swing_highs.append((df.index[i], highs[i]))
            if lows[i] == min(lows[i-window:i+window+1]):
                swing_lows.append((df.index[i], lows[i]))
        return swing_highs, swing_lows

    def analyze(self, df):
        if len(df) < 30:
            return []
        swing_highs, swing_lows = self._find_swing_highs_lows(df, window=5)
        close = df["Close"].iloc[-1]
        signals = []

        # Buy-side liquidity: recent swing highs above price
        bsl = [p for _, p in swing_highs if p > close]
        if bsl:
            nearest_bsl = min(bsl)
            dist_pct = (nearest_bsl - close) / close * 100
            if dist_pct < 3:
                signals.append({
                    "type": "BSL_NEAR",
                    "direction": "SHORT",
                    "confidence": min(50 + int((3 - dist_pct) * 10), 75),
                    "detail": f"BSL at {nearest_bsl:.2f} dist={dist_pct:.1f}%"
                })

        # Sell-side liquidity: recent swing lows below price
        ssl = [p for _, p in swing_lows if p < close]
        if ssl:
            nearest_ssl = max(ssl)
            dist_pct = (close - nearest_ssl) / close * 100
            if dist_pct < 3:
                signals.append({
                    "type": "SSL_NEAR",
                    "direction": "LONG",
                    "confidence": min(50 + int((3 - dist_pct) * 10), 75),
                    "detail": f"SSL at {nearest_ssl:.2f} dist={dist_pct:.1f}%"
                })

        # Equal highs (double top liquidity)
        if len(swing_highs) >= 2:
            last_two = [p for _, p in swing_highs[-2:]]
            if abs(last_two[0] - last_two[1]) / last_two[0] < 0.005:
                signals.append({
                    "type": "EQUAL_HIGHS",
                    "direction": "SHORT",
                    "confidence": 55,
                    "detail": f"Equal highs at {last_two[0]:.2f} and {last_two[1]:.2f}"
                })

        # Equal lows (double bottom)
        if len(swing_lows) >= 2:
            last_two = [p for _, p in swing_lows[-2:]]
            if abs(last_two[0] - last_two[1]) / last_two[0] < 0.005:
                signals.append({
                    "type": "EQUAL_LOWS",
                    "direction": "LONG",
                    "confidence": 55,
                    "detail": f"Equal lows at {last_two[0]:.2f} and {last_two[1]:.2f}"
                })

        return signals