"""
Dow Theory — Trend Detection via HH/HL and LH/LL
"""
import numpy as np
import pandas as pd

class DowDetector:
    """Detects primary trend direction using swing highs/lows."""

    def __init__(self, swing_window=20):
        self.swing_window = swing_window

    def _swing_highs_lows(self, df):
        """Find swing highs and lows."""
        highs = df["High"].values
        lows = df["Low"].values
        swing_highs = []
        swing_lows = []
        for i in range(2, len(df) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                swing_highs.append((df.index[i], highs[i]))
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                swing_lows.append((df.index[i], lows[i]))
        return swing_highs, swing_lows

    def analyze(self, df):
        if len(df) < 30:
            return []
        swing_highs, swing_lows = self._swing_highs_lows(df)
        if len(swing_highs) < 3 or len(swing_lows) < 3:
            return []

        recent_sh = [p for _, p in swing_highs[-5:]]
        recent_sl = [p for _, p in swing_lows[-5:]]

        hh = len(recent_sh) >= 2 and recent_sh[-1] > recent_sh[-2]
        hl = len(recent_sl) >= 2 and recent_sl[-1] > recent_sl[-2]
        lh = len(recent_sh) >= 2 and recent_sh[-1] < recent_sh[-2]
        ll = len(recent_sl) >= 2 and recent_sl[-1] < recent_sl[-2]

        signals = []
        if hh and hl:
            conf = 50 + (len(recent_sh) * 5)
            signals.append({
                "type": "TREND_UP",
                "direction": "LONG",
                "confidence": min(conf, 90),
                "detail": f"Dow uptrend: HH={hh} HL={hl}"
            })
        elif lh and ll:
            conf = 50 + (len(recent_sh) * 5)
            signals.append({
                "type": "TREND_DOWN",
                "direction": "SHORT",
                "confidence": min(conf, 90),
                "detail": f"Dow downtrend: LH={lh} LL={ll}"
            })
        else:
            signals.append({
                "type": "TREND_SIDEWAYS",
                "direction": "NEUTRAL",
                "confidence": 30,
                "detail": "No clear trend structure"
            })
        return signals
