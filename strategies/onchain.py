"""
On-Chain Analysis — Supply/Demand Metrics (proxy from exchange data)
"""
import numpy as np
import pandas as pd

class OnChainDetector:
    """On-chain proxy signals from exchange activity (volume, velocity, whale estimation)."""

    def analyze(self, df):
        if len(df) < 30:
            return []
        recent = df.tail(30).copy()
        vol = recent["Volume"]
        close = recent["Close"]

        vol_ma5 = vol.rolling(5).mean()
        vol_ma20 = vol.rolling(20).mean()
        vol_ratio = vol_ma5.iloc[-1] / vol_ma20.iloc[-1]

        signals = []

        if vol_ratio > 2.0:
            signals.append({
                "type": "ONCHAIN_VOLUME_SPIKE",
                "direction": "SHORT" if close.iloc[-1] < close.iloc[-5] else "LONG",
                "confidence": 55,
                "detail": f"Volume spike: 5MA/20MA={vol_ratio:.2f}"
            })

        if vol_ratio < 0.5:
            signals.append({
                "type": "ONCHAIN_VOLUME_DROUGHT",
                "direction": "LONG",
                "confidence": 45,
                "detail": f"Volume drought: 5MA/20MA={vol_ratio:.2f}"
            })

        recent.loc[:, "Body"] = abs(recent["Close"] - recent["Open"])
        avg_body = recent["Body"].mean()
        last_body = recent["Body"].iloc[-1]
        if last_body > avg_body * 3:
            signals.append({
                "type": "ONCHAIN_WHALE_CANDLE",
                "direction": "LONG" if recent["Close"].iloc[-1] > recent["Open"].iloc[-1] else "SHORT",
                "confidence": 60,
                "detail": f"Whale candle: body {last_body:.4f} vs avg {avg_body:.4f}"
            })

        if close.iloc[-1] < close.iloc[-3] and vol.iloc[-1] > vol.iloc[-3]:
            signals.append({
                "type": "ONCHAIN_EXCHANGE_INFLOW",
                "direction": "SHORT",
                "confidence": 50,
                "detail": "Price down, volume up — potential distribution"
            })
        elif close.iloc[-1] > close.iloc[-3] and vol.iloc[-1] < vol.iloc[-3]:
            signals.append({
                "type": "ONCHAIN_EXCHANGE_OUTFLOW",
                "direction": "LONG",
                "confidence": 50,
                "detail": "Price up, volume down — potential accumulation"
            })

        return signals