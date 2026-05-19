"""
Order Block / Institutional Flow — Bullish & Bearish Order Blocks + Breaker Blocks
"""
import numpy as np
import pandas as pd

class InstitutionalOBDetector:
    """Detects institutional order blocks and breaker blocks from price action."""

    def _find_obs(self, df):
        """Find standard order blocks — last candle before strong move."""
        obs = []
        for i in range(2, len(df) - 3):
            curr = df.iloc[i]
            n1 = df.iloc[i + 1]
            n2 = df.iloc[i + 2]
            n3 = df.iloc[i + 3]
            avg_move = abs(df["Close"].diff()).mean()

            move = abs(n3["Close"] - n1["Close"])
            if move < avg_move * 1.5:
                continue

            if n2["Close"] > n3["Close"]:  # bearish move after OB
                obs.append({
                    "type": "BEARISH_OB",
                    "high": curr["High"],
                    "low": curr["Low"],
                    "strength": move / avg_move,
                    "idx": df.index[i]
                })
            else:
                obs.append({
                    "type": "BULLISH_OB",
                    "high": curr["High"],
                    "low": curr["Low"],
                    "strength": move / avg_move,
                    "idx": df.index[i]
                })
        return obs

    def _find_breakers(self, df):
        """Find breaker blocks — OB that has been broken and flipped."""
        obs = self._find_obs(df)
        breakers = []
        close = df["Close"].values
        for ob in obs:
            ob_idx = list(df.index).index(ob["idx"]) if ob["idx"] in df.index else -1
            if ob_idx < 0 or ob_idx >= len(close) - 3:
                continue
            subsequent = close[ob_idx+3:]
            if len(subsequent) < 5:
                continue
            if ob["type"] == "BULLISH_OB" and subsequent.min() < ob["low"]:
                breakers.append({**ob, "breaker_type": "BEARISH_BREAKER"})
            elif ob["type"] == "BEARISH_OB" and subsequent.max() > ob["high"]:
                breakers.append({**ob, "breaker_type": "BULLISH_BREAKER"})
        return breakers

    def analyze(self, df):
        if len(df) < 30:
            return []
        close_price = df["Close"].iloc[-1]
        signals = []

        obs = self._find_obs(df)
        for ob in obs[-5:]:
            if ob["low"] <= close_price <= ob["high"]:
                dir = "LONG" if ob["type"] == "BULLISH_OB" else "SHORT"
                signals.append({
                    "type": f"INST_OB_{ob['type']}",
                    "direction": dir,
                    "confidence": min(50 + int(ob["strength"] * 5), 80),
                    "detail": f"OB hit: [{ob['low']:.2f}-{ob['high']:.2f}]"
                })

        breakers = self._find_breakers(df)
        for bk in breakers[-3:]:
            if bk["low"] <= close_price <= bk["high"]:
                dir = "LONG" if "BULLISH" in bk["breaker_type"] else "SHORT"
                signals.append({
                    "type": f"INST_BREAKER_{bk['breaker_type']}",
                    "direction": dir,
                    "confidence": 60,
                    "detail": f"Breaker: [{bk['low']:.2f}-{bk['high']:.2f}]"
                })

        return signals