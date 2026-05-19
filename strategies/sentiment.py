"""
Sentiment Analysis — Fear & Greed Proxy, Volume Extremes, Funding Rate Proxy
"""
import numpy as np
import pandas as pd

class SentimentDetector:
    """Sentiment signals from price/volume extremes (proxy for F&G, funding)."""

    def analyze(self, df):
        if len(df) < 30:
            return []
        recent = df.tail(30)
        close = recent["Close"]
        vol = recent["Volume"]
        returns = close.pct_change()

        signals = []

        # Volatility-based sentiment: sharp moves = extreme sentiment
        daily_ret = returns.tail(5)
        abs_returns = daily_ret.abs()
        avg_abs = abs_returns.mean()

        if len(abs_returns) > 0:
            last_abs = abs_returns.iloc[-1] if not abs_returns.empty else 0
            if last_abs > avg_abs * 2:
                direction = "LONG" if daily_ret.iloc[-1] > 0 else "SHORT"
                signals.append({
                    "type": "SENTIMENT_EXTREME_MOVE",
                    "direction": direction,
                    "confidence": 50,
                    "detail": f"Extreme move: {daily_ret.iloc[-1]*100:.1f}% (2x avg)"
                })

        # Contrarian: extreme volume w/ small move = exhaustion
        if len(vol) >= 5:
            vol_ma = vol.tail(5).mean()
            last_vol = vol.iloc[-1]
            last_ret = returns.iloc[-1] if not returns.empty else 0
            if last_vol > vol_ma * 2 and abs(last_ret) < 0.005:
                signals.append({
                    "type": "SENTIMENT_EXHAUSTION",
                    "direction": "LONG" if last_ret < 0 else "SHORT",
                    "confidence": 55,
                    "detail": f"Exhaustion: high vol, small move ({last_ret*100:.2f}%)"
                })

        # Funding rate proxy: sustained direction with increasing vol = overheated
        if len(df) >= 20:
            ret_5 = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100
            vol_trend = vol.iloc[-5:].mean() / vol.iloc[-20:-5].mean()
            if abs(ret_5) > 3 and vol_trend > 1.3:
                direction = "SHORT" if ret_5 > 0 else "LONG"
                signals.append({
                    "type": "SENTIMENT_OVERHEATED",
                    "direction": direction,
                    "confidence": 55,
                    "detail": f"Overheated: {ret_5:.1f}% move, vol trend={vol_trend:.2f}"
                })

        return signals