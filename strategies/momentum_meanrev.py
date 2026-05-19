"""
Momentum & Mean Reversion Combo — Trend + Pullback Entries
"""
import numpy as np
import pandas as pd

class MomentumMeanRevDetector:
    """Combines momentum (trend following) with mean reversion (pullback entries)."""

    def _rsi(self, series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    def analyze(self, df):
        if len(df) < 30:
            return []
        close = df["Close"]
        rsi = self._rsi(close)
        last_rsi = rsi.iloc[-1]

        # Trend detection via moving averages
        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean() if len(close) >= 50 else None
        sma100 = close.rolling(100).mean() if len(close) >= 100 else None

        signals = []

        # Determine trend
        uptrend = close.iloc[-1] > sma20.iloc[-1]
        if sma50 is not None:
            uptrend = uptrend and sma20.iloc[-1] > sma50.iloc[-1]
        if sma100 is not None:
            uptrend = uptrend and sma50.iloc[-1] > sma100.iloc[-1]

        downtrend = close.iloc[-1] < sma20.iloc[-1]
        if sma50 is not None:
            downtrend = downtrend and sma20.iloc[-1] < sma50.iloc[-1]
        if sma100 is not None:
            downtrend = downtrend and sma50.iloc[-1] < sma100.iloc[-1]

        # Momentum signal in direction of trend
        if uptrend and last_rsi > 50:
            signals.append({
                "type": "MOMENTUM_UPTREND",
                "direction": "LONG",
                "confidence": min(50 + int((last_rsi - 50) * 0.5), 75),
                "detail": f"Uptrend momentum: RSI={last_rsi:.1f}"
            })

        if downtrend and last_rsi < 50:
            signals.append({
                "type": "MOMENTUM_DOWNTREND",
                "direction": "SHORT",
                "confidence": min(50 + int((50 - last_rsi) * 0.5), 75),
                "detail": f"Downtrend momentum: RSI={last_rsi:.1f}"
            })

        # Mean reversion pullback entry in trending market
        if uptrend and last_rsi < 35:
            signals.append({
                "type": "MR_PULLBACK_LONG",
                "direction": "LONG",
                "confidence": min(55 + int((35 - last_rsi) * 2), 85),
                "detail": f"Pullback long in uptrend: RSI={last_rsi:.1f}"
            })

        if downtrend and last_rsi > 65:
            signals.append({
                "type": "MR_PULLBACK_SHORT",
                "direction": "SHORT",
                "confidence": min(55 + int((last_rsi - 65) * 2), 85),
                "detail": f"Pullback short in downtrend: RSI={last_rsi:.1f}"
            })

        # Reversal at extremes
        if last_rsi > 80:
            signals.append({
                "type": "MR_REVERSAL_SHORT",
                "direction": "SHORT",
                "confidence": 60,
                "detail": f"RSI extreme: {last_rsi:.1f} > 80"
            })
        elif last_rsi < 20:
            signals.append({
                "type": "MR_REVERSAL_LONG",
                "direction": "LONG",
                "confidence": 60,
                "detail": f"RSI extreme: {last_rsi:.1f} < 20"
            })

        return signals