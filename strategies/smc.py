"""
ICT / Smart Money Concepts (SMC) — FVG, Order Block, Liquidity Sweep, MSS
"""
import numpy as np
import pandas as pd

class SMCDetector:
    """Detects ICT/SMC concepts from OHLCV data."""

    def _find_fvg(self, df):
        """Find Fair Value Gaps (3-candle imbalance)."""
        fvgs = []
        for i in range(1, len(df) - 1):
            prev = df.iloc[i - 1]
            curr = df.iloc[i]
            next_c = df.iloc[i + 1]

            # Bullish FVG: gap up (next low > prev high)
            if next_c["Low"] > prev["High"]:
                fvgs.append({
                    "idx": df.index[i],
                    "type": "BULLISH_FVG",
                    "level": (prev["High"] + next_c["Low"]) / 2,
                    "top": next_c["Low"],
                    "bottom": prev["High"]
                })
            # Bearish FVG: gap down (next high < prev low)
            if next_c["High"] < prev["Low"]:
                fvgs.append({
                    "idx": df.index[i],
                    "type": "BEARISH_FVG",
                    "level": (prev["Low"] + next_c["High"]) / 2,
                    "top": prev["Low"],
                    "bottom": next_c["High"]
                })
        return fvgs

    def _find_order_blocks(self, df):
        """Find order blocks — last candle before a strong move."""
        blocks = []
        for i in range(2, len(df) - 2):
            curr = df.iloc[i]
            next1 = df.iloc[i + 1]
            next2 = df.iloc[i + 2]
            move = abs(next2["Close"] - next1["Close"])
            avg_move = abs(df["Close"].diff()).mean()

            if move > avg_move * 2:
                if next2["Close"] > next2["Open"]:  # Bullish move
                    blocks.append({
                        "idx": df.index[i],
                        "type": "BULLISH_OB",
                        "high": curr["High"],
                        "low": curr["Low"],
                        "strength": move / avg_move
                    })
                else:  # Bearish move
                    blocks.append({
                        "idx": df.index[i],
                        "type": "BEARISH_OB",
                        "high": curr["High"],
                        "low": curr["Low"],
                        "strength": move / avg_move
                    })
        return blocks

    def _find_liquidity_sweeps(self, df):
        """Find liquidity sweeps — price breaking then reversing from swing high/low."""
        swings = []
        for i in range(5, len(df) - 5):
            if df["High"].iloc[i] > max(df["High"].iloc[i-5:i]) and df["High"].iloc[i] > max(df["High"].iloc[i+1:i+6]):
                swings.append(("high", df.index[i], df["High"].iloc[i]))
            if df["Low"].iloc[i] < min(df["Low"].iloc[i-5:i]) and df["Low"].iloc[i] < min(df["Low"].iloc[i+1:i+6]):
                swings.append(("low", df.index[i], df["Low"].iloc[i]))

        sweeps = []
        recent = df.tail(10)
        for typ, idx, price in swings[-3:]:
            if typ == "high":
                if recent["Low"].min() < price and recent["Close"].iloc[-1] > price:
                    sweeps.append({"type": "LIQ_SWEEP_BSL", "direction": "LONG", "level": price})
            if typ == "low":
                if recent["High"].max() > price and recent["Close"].iloc[-1] < price:
                    sweeps.append({"type": "LIQ_SWEEP_SSL", "direction": "SHORT", "level": price})
        return sweeps

    def analyze(self, df):
        if len(df) < 30:
            return []
        signals = []
        close = df["Close"].iloc[-1]

        # Fair Value Gaps
        fvgs = self._find_fvg(df)
        for fvg in fvgs[-3:]:
            if fvg["bottom"] <= close <= fvg["top"]:
                dir = "LONG" if fvg["type"] == "BULLISH_FVG" else "SHORT"
                signals.append({
                    "type": f"SMC_{fvg['type']}",
                    "direction": dir,
                    "confidence": 55,
                    "detail": f"FVG hit: [{fvg['bottom']:.2f}-{fvg['top']:.2f}]"
                })

        # Order Blocks
        obs = self._find_order_blocks(df)
        for ob in obs[-3:]:
            if ob["low"] <= close <= ob["high"]:
                dir = "LONG" if ob["type"] == "BULLISH_OB" else "SHORT"
                signals.append({
                    "type": f"SMC_{ob['type']}",
                    "direction": dir,
                    "confidence": min(50 + int(ob["strength"] * 5), 80),
                    "detail": f"OB touched: [{ob['low']:.2f}-{ob['high']:.2f}]"
                })

        # Liquidity Sweeps
        sweeps = self._find_liquidity_sweeps(df)
        for sw in sweeps:
            signals.append({
                "type": f"SMC_{sw['type']}",
                "direction": sw["direction"],
                "confidence": 60,
                "detail": f"Liq sweep: {sw['type']} at {sw['level']:.2f}"
            })

        return signals