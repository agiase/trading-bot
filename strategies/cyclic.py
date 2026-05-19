"""
Cyclic / Seasonal Analysis — Halving Cycles, Monthly/Weekly Seasonality
"""
import numpy as np
import pandas as pd

class CyclicDetector:
    """Detects cyclic patterns: weekly seasonality, month-end effects."""

    def analyze(self, df):
        if len(df) < 14:
            return []
        signals = []

        # Weekly seasonality: check day-of-week patterns
        close = df["Close"]
        if len(close) >= 7:
            week_close = close.tail(7).values
            week_high = df["High"].tail(7).max()
            week_low = df["Low"].tail(7).min()
            week_range = (week_high - week_low) / week_low * 100

            # Strong week range suggests continuation
            if week_range > 5:
                signals.append({
                    "type": "CYCLIC_WIDE_WEEK",
                    "direction": "LONG" if week_close[-1] > week_close[0] else "SHORT",
                    "confidence": 50,
                    "detail": f"Wide weekly range: {week_range:.1f}%"
                })

        # Bi-weekly cycle (14-day)
        if len(df) >= 14:
            c14 = close.iloc[-14]
            c7 = close.iloc[-7]
            c0 = close.iloc[-1]
            # If price higher than 14d ago but lower than 7d ago = possible top
            if c0 > c14 and c0 < c7:
                signals.append({
                    "type": "CYCLIC_14D_PULLBACK",
                    "direction": "SHORT",
                    "confidence": 40,
                    "detail": "14-day cycle: high then pullback"
                })
            elif c0 < c14 and c0 > c7:
                signals.append({
                    "type": "CYCLIC_14D_BOUNCE",
                    "direction": "LONG",
                    "confidence": 40,
                    "detail": "14-day cycle: low then bounce"
                })

        # Month-end effect (check rolling 30-day extremes)
        if len(df) >= 30:
            high_30 = df["High"].tail(30).max()
            low_30 = df["Low"].tail(30).min()
            current = close.iloc[-1]
            range_pos = (current - low_30) / (high_30 - low_30) if high_30 != low_30 else 0.5
            if range_pos > 0.85:
                signals.append({
                    "type": "CYCLIC_MONTH_END_TOP",
                    "direction": "SHORT",
                    "confidence": 45,
                    "detail": f"Month-end top: range position {range_pos:.0%}"
                })
            elif range_pos < 0.15:
                signals.append({
                    "type": "CYCLIC_MONTH_END_BOTTOM",
                    "direction": "LONG",
                    "confidence": 45,
                    "detail": f"Month-end bottom: range position {range_pos:.0%}"
                })

        return signals