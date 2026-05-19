"""
Volume Spread Analysis (VSA) — Volume + Spread + Close Relationship
"""
import numpy as np
import pandas as pd

class VSADetector:
    """Detects VSA signals: no demand, stopping volume, upthrust, spring."""

    def analyze(self, df):
        if len(df) < 30:
            return []
        df = df.copy()
        df["Spread"] = df["High"] - df["Low"]
        df["VolSMA"] = df["Volume"].rolling(10).mean()
        df["SpreadSMA"] = df["Spread"].rolling(10).mean()
        recent = df.tail(20)
        signals = []

        last = recent.iloc[-1]
        prev = recent.iloc[-2]

        # Stopping volume: wide spread, high volume, small net price change
        if (last["Volume"] > last["VolSMA"] * 1.5 and
            last["Spread"] > last["SpreadSMA"] * 1.3 and
            abs(last["Close"] - last["Open"]) / last["Spread"] < 0.3):
            signals.append({
                "type": "VSA_STOPPING_VOLUME",
                "direction": "NEUTRAL",
                "confidence": 65,
                "detail": f"Stopping volume: vol={last['Volume']:.0f} spread={last['Spread']:.4f}"
            })

        # No demand: up bar, narrow spread, low volume (bull trap)
        if (last["Close"] > last["Open"] and
            last["Spread"] < last["SpreadSMA"] * 0.7 and
            last["Volume"] < last["VolSMA"] * 0.7):
            signals.append({
                "type": "VSA_NO_DEMAND",
                "direction": "SHORT",
                "confidence": 60,
                "detail": f"No demand: up bar, narrow spread, low vol"
            })

        # Upthrust: tests high area, closes weak
        if (last["High"] > recent["High"].iloc[:-1].max() * 0.99 and
            last["Close"] < last["Open"]):
            signals.append({
                "type": "VSA_UPTHRUST",
                "direction": "SHORT",
                "confidence": 60,
                "detail": f"Upthrust: new high, closes weak"
            })

        # Spring: tests low area, closes strong
        if (last["Low"] < recent["Low"].iloc[:-1].min() * 1.01 and
            last["Close"] > last["Open"]):
            signals.append({
                "type": "VSA_SPRING",
                "direction": "LONG",
                "confidence": 60,
                "detail": f"Spring: new low, closes strong"
            })

        return signals