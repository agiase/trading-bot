"""
Supply & Demand Zones — Drop Base Rally, Rally Base Drop
"""
import numpy as np
import pandas as pd

class SupplyDemandDetector:
    """Detects supply and demand zones from swing points."""

    def __init__(self, zone_lookback=30):
        self.zone_lookback = zone_lookback

    def _find_zones(self, df):
        """Find RBR (demand) and RBD (supply) zones."""
        highs = df["High"].values
        lows = df["Low"].values
        closes = df["Close"].values
        zones = []

        for i in range(5, len(df) - 5):
            # Demand zone (DBR): drop, base (tight range), rally
            if lows[i] == min(lows[i-5:i+6]):
                pre = closes[i-5:i]
                post = closes[i+1:i+6]
                if min(pre) > lows[i] and max(post) > max(closes[i-3:i+1]):
                    zones.append({
                        "type": "DEMAND",
                        "base_low": lows[i],
                        "base_high": max(df["High"].iloc[i-2:i+3]),
                        "strength": len([c for c in post if c > max(closes[i-3:i+1])])
                    })

            # Supply zone (RBD): rally, base, drop
            if highs[i] == max(highs[i-5:i+6]):
                pre = closes[i-5:i]
                post = closes[i+1:i+6]
                if max(pre) < highs[i] and min(post) < min(closes[i-3:i+1]):
                    zones.append({
                        "type": "SUPPLY",
                        "base_low": min(df["Low"].iloc[i-2:i+3]),
                        "base_high": highs[i],
                        "strength": len([c for c in post if c < min(closes[i-3:i+1])])
                    })
        return zones

    def analyze(self, df):
        if len(df) < 30:
            return []
        zones = self._find_zones(df)
        close = df["Close"].iloc[-1]
        signals = []

        for zone in zones[-5:]:
            in_zone = zone["base_low"] <= close <= zone["base_high"]
            if not in_zone:
                continue

            if zone["type"] == "DEMAND":
                signals.append({
                    "type": "DEMAND_ZONE",
                    "direction": "LONG",
                    "confidence": min(50 + zone["strength"] * 10, 85),
                    "detail": f"Demand zone [{zone['base_low']:.2f}-{zone['base_high']:.2f}] strength={zone['strength']}"
                })
            else:
                signals.append({
                    "type": "SUPPLY_ZONE",
                    "direction": "SHORT",
                    "confidence": min(50 + zone["strength"] * 10, 85),
                    "detail": f"Supply zone [{zone['base_low']:.2f}-{zone['base_high']:.2f}] strength={zone['strength']}"
                })

        return signals