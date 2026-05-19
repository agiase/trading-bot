"""
Gann Theory — Gann Angles & Time Cycles
"""
import numpy as np
import pandas as pd

class GannDetector:
    """Detects Gann angle support/resistance and time cycle turning points."""

    def __init__(self):
        pass

    def _gann_angles(self, high, low, lookback=30):
        """Compute 1x1, 2x1, 1x2 angle levels."""
        price_range = high - low
        if price_range == 0:
            return {}
        step = price_range / lookback
        return {
            "1x1_angle": step,       # 45 degrees
            "2x1_angle": step * 2,    # steeper
            "1x2_angle": step / 2,    # shallower
        }

    def analyze(self, df):
        if len(df) < 30:
            return []
        recent = df.tail(30)
        high = recent["High"].max()
        low = recent["Low"].min()
        close = recent["Close"].iloc[-1]

        angles = self._gann_angles(high, low)
        signals = []

        # Check if price is near key angle levels
        for angle_name, angle_val in angles.items():
            if angle_val == 0:
                continue
            # Distance from high/low to angle lines
            dist_from_high = abs(close - (high - angle_val))
            dist_from_low = abs(close - (low + angle_val))
            threshold = (high - low) * 0.02

            if dist_from_high < threshold:
                signals.append({
                    "type": "GANN_RESISTANCE",
                    "direction": "SHORT",
                    "confidence": 55,
                    "detail": f"Price near {angle_name} resistance from high angle resistance"
                })
            if dist_from_low < threshold:
                signals.append({
                    "type": "GANN_SUPPORT",
                    "direction": "LONG",
                    "confidence": 55,
                    "detail": f"Price near {angle_name} low angle support"
                })

        # Time cycle check: look for turning points every 7, 14, 21 bars
        for cycle in [7, 14, 21]:
            if len(df) >= cycle:
                prev_close = df["Close"].iloc[-cycle]
                if abs(close - prev_close) / prev_close < 0.01:
                    signals.append({
                        "type": "GANN_TIME_CYCLE",
                        "direction": "NEUTRAL",
                        "confidence": 40,
                        "detail": f"Gann time cycle {cycle} bars — potential turn"
                    })

        return signals