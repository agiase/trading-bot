"""
Statistical Arbitrage / Pairs Trading — Cointegration & Z-Score
"""
import numpy as np
import pandas as pd

class StatArbDetector:
    """Single-ticker stat arb proxy: mean reversion z-score on returns."""

    def _zscore(self, series, window=20):
        mean = series.rolling(window).mean()
        std = series.rolling(window).std()
        return (series - mean) / std.replace(0, np.nan)

    def analyze(self, df):
        if len(df) < 30:
            return []
        close = df["Close"]
        returns = close.pct_change()
        z = self._zscore(returns, window=20)
        last_z = z.iloc[-1]
        signals = []

        if abs(last_z) > 2:
            direction = "LONG" if last_z < -2 else "SHORT"
            confidence = min(int(abs(last_z) * 15) + 40, 80)
            signals.append({
                "type": "STATARB_ZSCORE",
                "direction": direction,
                "confidence": confidence,
                "detail": f"Z-score={last_z:.2f} — extreme mean reversion"
            })
        elif abs(last_z) > 1.5:
            direction = "LONG" if last_z < -1.5 else "SHORT"
            confidence = min(int(abs(last_z) * 12) + 30, 60)
            signals.append({
                "type": "STATARB_ZSCORE",
                "direction": direction,
                "confidence": confidence,
                "detail": f"Z-score={last_z:.2f} — moderate mean reversion"
            })

        # Variance ratio test proxy: autocorrelation on returns
        if len(returns) >= 50:
            ac1 = returns.tail(50).autocorr(lag=1)
            if not np.isnan(ac1) and abs(ac1) < 0.05:
                signals.append({
                    "type": "STATARB_RANDOM_WALK",
                    "direction": "NEUTRAL",
                    "confidence": 30,
                    "detail": f"Near random walk: autocorr={ac1:.3f}"
                })

        return signals