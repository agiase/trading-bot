"""
Market Profile (TPO) — Value Area, POC, Range Structure
"""
import numpy as np
import pandas as pd

class MarketProfileDetector:
    """Detects value area, point of control, and day type from OHLCV."""

    def __init__(self, value_area_pct=0.70):
        self.value_area_pct = value_area_pct

    def _compute_value_area(self, df):
        """Estimate value area from volume distribution."""
        if "Volume" not in df.columns or df["Volume"].sum() == 0:
            return None, None, None
        prices = df["Close"].values
        vols = df["Volume"].values
        if len(prices) < 10:
            return None, None, None

        bins = 20
        price_min, price_max = prices.min(), prices.max()
        if price_max == price_min:
            return None, None, None
        bin_edges = np.linspace(price_min, price_max, bins + 1)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        vol_by_bin = np.zeros(bins)
        for p, v in zip(prices, vols):
            idx = np.digitize(p, bin_edges) - 1
            if 0 <= idx < bins:
                vol_by_bin[idx] += v

        poc_idx = np.argmax(vol_by_bin)
        poc = bin_centers[poc_idx]
        total_vol = vol_by_bin.sum()
        target_vol = total_vol * self.value_area_pct

        sorted_indices = sorted(range(bins), key=lambda i: vol_by_bin[i], reverse=True)
        cum_vol = 0
        va_low_idx = bins
        va_high_idx = 0
        for i in sorted_indices:
            cum_vol += vol_by_bin[i]
            va_low_idx = min(va_low_idx, i)
            va_high_idx = max(va_high_idx, i)
            if cum_vol >= target_vol:
                break

        va_low = bin_edges[va_low_idx]
        va_high = bin_edges[va_high_idx + 1]
        return poc, va_low, va_high

    def analyze(self, df):
        if len(df) < 20:
            return []
        recent = df.tail(48)
        poc, va_low, va_high = self._compute_value_area(recent)
        if poc is None:
            return []

        close = recent["Close"].iloc[-1]
        high = recent["High"].max()
        low = recent["Low"].min()
        range_pct = (high - low) / low * 100

        signals = []
        if range_pct > 3:
            signals.append({
                "type": "MARKET_PROFILE_TREND_DAY",
                "direction": "LONG" if close > va_high else "SHORT",
                "confidence": 55,
                "detail": f"Trend day: range={range_pct:.1f}% POC={poc:.2f} VA=[{va_low:.2f}-{va_high:.2f}]"
            })
        else:
            signals.append({
                "type": "MARKET_PROFILE_NORMAL_DAY",
                "direction": "NEUTRAL",
                "confidence": 35,
                "detail": f"Normal day: range={range_pct:.1f}% POC={poc:.2f} VA=[{va_low:.2f}-{va_high:.2f}]"
            })

        if close > va_high * 1.02:
            signals.append({
                "type": "VALUE_AREA_EXTENSION_UP",
                "direction": "NEUTRAL",
                "confidence": 45,
                "detail": f"Price above value area: {close:.2f} > {va_high:.2f}"
            })
        elif close < va_low * 0.98:
            signals.append({
                "type": "VALUE_AREA_EXTENSION_DOWN",
                "direction": "NEUTRAL",
                "confidence": 45,
                "detail": f"Price below value area: {close:.2f} < {va_low:.2f}"
            })

        return signals
