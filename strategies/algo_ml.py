"""
Algorithmic / ML Trading — Mean Reversion, Momentum, RSI, MACD
"""
import numpy as np
import pandas as pd

class MLDetector:
    """Statistical signals: mean reversion and momentum signals."""

    def _rsi(self, series, period=14):
        delta = series.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        return 100 - (100 / (1 + rs))

    def _macd(self, series):
        ema12 = series.ewm(span=12).mean()
        ema26 = series.ewm(span=26).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9).mean()
        return macd, signal

    def _bollinger(self, series, period=20):
        sma = series.rolling(period).mean()
        std = series.rolling(period).std()
        return sma + 2 * std, sma - 2 * std

    def analyze(self, df):
        if len(df) < 30:
            return []
        close = df["Close"]
        rsi = self._rsi(close)
        macd, macd_signal = self._macd(close)
        bb_upper, bb_lower = self._bollinger(close)

        last_rsi = rsi.iloc[-1]
        last_macd = macd.iloc[-1]
        last_macd_sig = macd_signal.iloc[-1]
        last_close = close.iloc[-1]
        last_bb_upper = bb_upper.iloc[-1]
        last_bb_lower = bb_lower.iloc[-1]

        signals = []

        # RSI oversold
        if last_rsi < 30:
            signals.append({
                "type": "RSI_OVERSOLD",
                "direction": "LONG",
                "confidence": min(50 + int((30 - last_rsi) * 2), 85),
                "detail": f"RSI={last_rsi:.1f} < 30"
            })
        # RSI overbought
        elif last_rsi > 70:
            signals.append({
                "type": "RSI_OVERBOUGHT",
                "direction": "SHORT",
                "confidence": min(50 + int((last_rsi - 70) * 2), 85),
                "detail": f"RSI={last_rsi:.1f} > 70"
            })

        # MACD crossover
        if last_macd > last_macd_sig and macd.iloc[-2] <= macd_signal.iloc[-2]:
            signals.append({
                "type": "MACD_CROSSOVER",
                "direction": "LONG",
                "confidence": 60,
                "detail": f"MACD bullish cross: {last_macd:.4f} > {last_macd_sig:.4f}"
            })
        elif last_macd < last_macd_sig and macd.iloc[-2] >= macd_signal.iloc[-2]:
            signals.append({
                "type": "MACD_CROSSOVER",
                "direction": "SHORT",
                "confidence": 60,
                "detail": f"MACD bearish cross: {last_macd:.4f} < {last_macd_sig:.4f}"
            })

        # Bollinger Band touch
        if last_close >= last_bb_upper:
            signals.append({
                "type": "BB_TOUCH_UPPER",
                "direction": "SHORT",
                "confidence": 55,
                "detail": f"Price at BB upper: {last_close:.2f} >= {last_bb_upper:.2f}"
            })
        elif last_close <= last_bb_lower:
            signals.append({
                "type": "BB_TOUCH_LOWER",
                "direction": "LONG",
                "confidence": 55,
                "detail": f"Price at BB lower: {last_close:.2f} <= {last_bb_lower:.2f}"
            })

        return signals