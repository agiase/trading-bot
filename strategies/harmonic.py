"""
Harmonic Patterns — Gartley, Butterfly, Bat, Crab via Fibonacci XABCD
"""
import numpy as np
import pandas as pd

class HarmonicDetector:
    """Detects harmonic patterns: Gartley, Butterfly, Bat, Crab."""

    HARMONIC_PATTERNS = {
        "GARTLEY": {"XA": None, "AB": 0.618, "BC": [0.382, 0.886], "CD": [1.13, 1.618]},
        "BUTTERFLY": {"XA": None, "AB": 0.786, "BC": [0.382, 0.886], "CD": [1.618, 2.618]},
        "BAT": {"XA": None, "AB": 0.382, "BC": [0.382, 0.886], "CD": [1.618, 2.618]},
        "CRAB": {"XA": None, "AB": 0.382, "BC": [0.382, 0.886], "CD": [2.618, 3.618]},
    }

    def _find_swings(self, df):
        highs = df["High"].values
        lows = df["Low"].values
        points = []
        for i in range(3, len(df) - 3):
            if highs[i] == max(highs[i-3:i+4]):
                points.append(("high", df.index[i], highs[i]))
            if lows[i] == min(lows[i-3:i+4]):
                points.append(("low", df.index[i], lows[i]))
        return points

    def analyze(self, df):
        if len(df) < 50:
            return []
        points = self._find_swings(df)
        if len(points) < 5:
            return []

        signals = []
        # Check XABCD structure from most recent swings
        for i in range(len(points) - 4):
            seg = points[i:i+5]
            types = [p[0] for p in seg]
            prices = [p[2] for p in seg]

            # Pattern: low-high-low-high-low (bullish) or high-low-high-low-high (bearish)
            if types != ["low", "high", "low", "high", "low"] and \
               types != ["high", "low", "high", "low", "high"]:
                continue

            # Calculate legs
            X, A, B, C, D = prices
            XA = abs(A - X)
            AB = abs(B - A)
            BC = abs(C - B)
            CD = abs(D - C)

            if XA == 0 or AB == 0 or BC == 0:
                continue

            AB_retrace = AB / XA
            BC_retrace = BC / AB
            CD_retrace = CD / BC

            for name, pattern in self.HARMONIC_PATTERNS.items():
                ab_target = pattern["AB"]
                bc_range = pattern["BC"]
                cd_range = pattern["CD"]

                if abs(AB_retrace - ab_target) > 0.05:
                    continue
                if not (bc_range[0] <= BC_retrace <= bc_range[1]):
                    continue
                if not (cd_range[0] <= CD_retrace <= cd_range[1]):
                    continue

                direction = "LONG" if types[0] == "low" else "SHORT"
                conf = min(60 + int((1 - abs(AB_retrace - ab_target)) * 30), 90)
                signals.append({
                    "type": f"HARMONIC_{name}",
                    "direction": direction,
                    "confidence": conf,
                    "detail": f"{name} at D={D:.4f}, legs: AB={AB_retrace:.3f} BC={BC_retrace:.3f} CD={CD_retrace:.3f}"
                })

        return signals