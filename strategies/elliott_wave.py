"""
Elliott Wave Theory — Impulse & Corrective Wave Detection
"""
import numpy as np
import pandas as pd

class ElliottWaveDetector:
    """Detects 5-wave impulse and 3-wave corrective patterns using swing structure + fib ratios."""

    def __init__(self):
        pass

    def _swing_points(self, df, window=5):
        highs = df["High"].values
        lows = df["Low"].values
        points = []
        for i in range(window, len(df) - window):
            if highs[i] == max(highs[i-window:i+window+1]):
                points.append((df.index[i], highs[i], "high"))
            if lows[i] == min(lows[i-window:i+window+1]):
                points.append((df.index[i], lows[i], "low"))
        return points

    def _fib_retrace(self, move, retrace_price):
        if move == 0:
            return 0
        return retrace_price / move

    def analyze(self, df):
        if len(df) < 50:
            return []
        points = self._swing_points(df)
        if len(points) < 8:
            return []

        # Look at last 8-10 swing points for wave structure
        recent = points[-10:]
        prices = [p[1] for p in recent]
        types = [p[2] for p in recent]

        # Check for 5-wave impulse: low-high-low-high-low (starting with low)
        # Wave 3 should not be shortest, wave 4 shouldn't overlap wave 1
        signals = []
        for start in range(len(recent) - 8):
            seg = recent[start:start+8]
            if len(seg) < 8:
                continue
            seg_types = [s[2] for s in seg]
            seg_prices = [s[1] for s in seg]

            # Pattern: low, high, low, high, low, high, low, high (impulse start low)
            if seg_types == ["low", "high", "low", "high", "low", "high", "low", "high"]:
                w1 = abs(seg_prices[1] - seg_prices[0])
                w2 = abs(seg_prices[2] - seg_prices[1])
                w3 = abs(seg_prices[3] - seg_prices[2])
                w4 = abs(seg_prices[4] - seg_prices[3])
                w5 = abs(seg_prices[5] - seg_prices[4])

                # Wave 3 not shortest
                if w3 < w1 or w3 < w5:
                    continue
                # Wave 2 not retrace 100% of 1
                if seg_prices[2] <= seg_prices[0]:
                    continue
                #4 not overlap 1
                if seg_prices[4] >= seg_prices[1]:
                    continue

                conf = 55 + int((w3 / max(w1, 0.01)) * 10)
                direction = "LONG" if seg_prices[-1] > seg_prices[0] else "SHORT"
                signals.append({
                    "type": "ELLIOTT_IMPULSE",
                    "direction": direction,
                    "confidence": min(conf, 95),
                    "detail": f"5-wave impulse detected. W3/W1={w3/w1:.2f}"
                })

            # Corrective ABC correction pattern
            if seg_types[:6] == ["high", "low", "high", "low", "high", "low"]:
                a = abs(seg_prices[1] - seg_prices[0])
                b = abs(seg_prices[2] - seg_prices[1])
                c = abs(seg_prices[3] - seg_prices[2])
                if b < a and abs(c - a) / max(a, 0.01) < 0.3:
                    signals.append({
                        "type": "ELLIOTT_ABC_CORRECTION",
                        "direction": "NEUTRAL",
                        "confidence": 50,
                        "detail": f"ABC correction: A={a:.2f} B={b:.2f} C={c:.2f}"
                    })

        return signals
