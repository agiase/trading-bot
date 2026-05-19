"""
Renko / Heikin-Ashi — Trend Smoothing & Noise Reduction
"""
import numpy as np
import pandas as pd

class RenkoDetector:
    """Simulates Renko bricks and Heikin-Ashi candles from OHLCV for trend signals."""

    def _heikin_ashi(self, df):
        """Compute Heikin-Ashi candles."""
        ha = df.copy()
        ha["HA_Close"] = (df["Open"] + df["High"] + df["Low"] + df["Close"]) / 4
        ha["HA_Open"] = ((df["Open"].shift(1) + df["Close"].shift(1)) / 2)
        ha["HA_Open"].iloc[0] = (df["Open"].iloc[0] + df["Close"].iloc[0]) / 2
        ha["HA_High"] = ha[["HA_Open", "HA_Close", "High"]].max(axis=1)
        ha["HA_Low"] = ha[["HA_Open", "HA_Close", "Low"]].min(axis=1)
        return ha

    def _renko_bricks(self, df, brick_size_pct=0.5):
        """Simulate Renko bricks from close prices."""
        brick_size = df["Close"].mean() * (brick_size_pct / 100)
        if brick_size == 0:
            return [], 0
        closes = df["Close"].values
        bricks = []
        prev_brick_close = closes[0]
        for c in closes[1:]:
            change = c - prev_brick_close
            num_bricks = int(abs(change) / brick_size)
            if num_bricks >= 1:
                direction = 1 if change > 0 else -1
                for _ in range(num_bricks):
                    prev_brick_close += direction * brick_size
                    bricks.append(direction)
        return bricks, brick_size

    def analyze(self, df):
        if len(df) < 30:
            return []
        signals = []

        ha = self._heikin_ashi(df)
        ha_tail = ha.tail(5)
        ha_bullish = ha_tail[ha_tail["HA_Close"] >= ha_tail["HA_Open"]]
        ha_bearish = ha_tail[ha_tail["HA_Close"] < ha_tail["HA_Open"]]

        if len(ha_bullish) >= 4:
            signals.append({
                "type": "HA_STRONG_UPTREND",
                "direction": "LONG",
                "confidence": 70,
                "detail": f"HA strong uptrend: {len(ha_bullish)}/5 bullish candles"
            })
        elif len(ha_bearish) >= 4:
            signals.append({
                "type": "HA_STRONG_DOWNTREND",
                "direction": "SHORT",
                "confidence": 70,
                "detail": f"HA strong downtrend: {len(ha_bearish)}/5 bearish candles"
            })
        elif len(ha_bullish) >= 3:
            signals.append({
                "type": "HA_UPTREND",
                "direction": "LONG",
                "confidence": 55,
                "detail": f"HA uptrend: {len(ha_bullish)}/5 bullish"
            })
        elif len(ha_bearish) >= 3:
            signals.append({
                "type": "HA_DOWNTREND",
                "direction": "SHORT",
                "confidence": 55,
                "detail": f"HA downtrend: {len(ha_bearish)}/5 bearish"
            })

        bricks, brick_size = self._renko_bricks(df, brick_size_pct=0.5)
        if len(bricks) >= 5:
            recent_bricks = bricks[-10:]
            up_bricks = sum(1 for b in recent_bricks if b > 0)
            down_bricks = len(recent_bricks) - up_bricks
            if up_bricks > down_bricks * 2:
                signals.append({
                    "type": "RENKO_UPTREND",
                    "direction": "LONG",
                    "confidence": 65,
                    "detail": f"Renko: {up_bricks}/{len(recent_bricks)} up bricks"
                })
            elif down_bricks > up_bricks * 2:
                signals.append({
                    "type": "RENKO_DOWNTREND",
                    "direction": "SHORT",
                    "confidence": 65,
                    "detail": f"Renko: {down_bricks}/{len(recent_bricks)} down bricks"
                })

        return signals