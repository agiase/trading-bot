"""
Order Flow / Tape Reading — CVD, Delta, Bid/Ask Imbalance Estimation
"""
import numpy as np
import pandas as pd

class OrderFlowDetector:
    """Estimates order flow from OHLCV — delta, CVD proxy, absorption."""

    def __init__(self):
        pass

    def _estimate_delta(self, df):
        """Estimate buying/selling pressure from candle wicks + close position."""
        df = df.copy()
        df["Body"] = abs(df["Close"] - df["Open"])
        df["UpperWick"] = df["High"] - df[["Close", "Open"]].max(axis=1)
        df["LowerWick"] = df[["Close", "Open"]].min(axis=1) - df["Low"]
        df["Delta"] = np.where(
            df["Close"] > df["Open"],
            df["Body"] + df["LowerWick"] - df["UpperWick"],
            -(df["Body"] + df["UpperWick"] - df["LowerWick"])
        )
        return df

    def analyze(self, df):
        if len(df) < 30:
            return []
        df = self._estimate_delta(df)
        recent = df.tail(20)
        cum_delta = recent["Delta"].sum()
        avg_delta = recent["Delta"].mean()
        delta_std = recent["Delta"].std()
        last_delta = recent["Delta"].iloc[-1]

        signals = []

        # Strong buying pressure
        if cum_delta > 0 and last_delta > 0 and avg_delta > delta_std * 0.5:
            signals.append({
                "type": "ORDER_FLOW_BUYING",
                "direction": "LONG",
                "confidence": min(50 + abs(cum_delta) * 2, 85),
                "detail": f"Cum delta={cum_delta:.4f} last={last_delta:.4f} avg={avg_delta:.4f}"
            })

        # Strong selling pressure
        if cum_delta < 0 and last_delta < 0 and abs(avg_delta) > delta_std * 0.5:
            signals.append({
                "type": "ORDER_FLOW_SELLING",
                "direction": "SHORT",
                "confidence": min(50 + abs(cum_delta) * 2, 85),
                "detail": f"Cum delta={cum_delta:.4f} last={last_delta:.4f} avg={avg_delta:.4f}"
            })

        # Absorption: wide range, small net delta (battle)
        recent_range = (recent["High"].max() - recent["Low"].min()) / recent["Low"].min() * 100
        if recent_range > 2 and abs(cum_delta) < delta_std:
            signals.append({
                "type": "ORDER_FLOW_ABSORPTION",
                "direction": "NEUTRAL",
                "confidence": 40,
                "detail": f"Absorption: range={recent_range:.2f}% cum_delta near zero"
            })

        return signals