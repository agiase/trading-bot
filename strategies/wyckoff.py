"""
Wyckoff Method — Accumulation & Distribution Detection
"""
import numpy as np
import pandas as pd

class WyckoffDetector:
    """
    Detects Wyckoff phases: Accumulation (SC→AR→ST→Spring→SOS/LPS)
    and Distribution (BC→AR→SOW→LPSY→LOT).
    """

    def __init__(self, atr_period=14, volume_smoothing=5):
        self.atr_period = atr_period
        self.volume_smoothing = volume_smoothing

    def compute_features(self, df):
        """Add Wyckoff-relevant indicators."""
        df = df.copy()
        df["ATR"] = self._atr(df, self.atr_period)
        df["Volume_SMA"] = df["Volume"].rolling(window=self.volume_smoothing).mean()
        df["Volume_Spike"] = df["Volume"] > df["Volume_SMA"] * 1.5
        df["HV"] = df["High"].rolling(10).max()
        df["LW"] = df["Low"].rolling(10).min()
        df["Range"] = df["HV"] - df["LW"]
        df["ClosePos"] = (df["Close"] - df["LW"]) / df["Range"].replace(0, np.nan)
        return df

    def detect_accumulation(self, df):
        """Detect Wyckoff Accumulation pattern."""
        df = self.compute_features(df)
        if len(df) < 25:
            return None, 0

        recent = df.tail(20)
        segment = df.tail(40).copy()

        # 1. Selling Climax (SC): high volume, wide spread down, then reversal
        sc_candidates = segment[segment["Volume_Spike"] &
                                 (segment["Close"] < segment["Close"].shift(1))].tail(5)
        if len(sc_candidates) == 0:
            return None, 0

        sc_idx = sc_candidates.index[-1]
        sc_loc = segment.index.get_loc(sc_idx)
        if sc_loc >= len(segment) - 2:
            return None, 0

        sc_price = segment.loc[sc_idx, "Close"]
        sc_vol = segment.loc[sc_idx, "Volume"]

        # 2. Automatic Rally (AR): price lifts after SC
        ar_segment = segment.iloc[sc_loc+1:]
        if len(ar_segment) < 3:
            return None, 0
        ar_high = ar_segment["High"].max()
        ar_idx = ar_segment["High"].idxmax()
        ar_rally_pct = (ar_high - sc_price) / sc_price * 100

        if ar_rally_pct < 3:
            return None, 0

        # 3. Secondary Test (ST): price revisits SC area, decreasing volume
        st_segment = ar_segment.loc[ar_idx:]
        if len(st_segment) < 3:
            return None, 0
        st_low = st_segment["Low"].min()
        st_idx = st_segment["Low"].idxmin()
        st_vol = st_segment.loc[st_idx, "Volume"]

        st_valid = (st_vol < sc_vol * 0.8) and (abs(st_low - sc_price) / sc_price < 0.05)

        # 4. Spring / shakeout
        spring = st_segment.iloc[2:]["Low"].min() < sc_price * 0.97 if len(st_segment) > 5 else False

        # 5. Sign of Strength (SOS): breakout above AR with volume
        test_segment = st_segment.loc[st_idx:]
        if len(test_segment) < 5:
            return None, 0
        sos_break = test_segment[test_segment["Close"] > ar_high * 0.995]
        sos_valid = len(sos_break) > 0

        if not sc_valid:
            return None, 0

        # --- Score ---
        score = 0
        score += 25  # SC detected
        if ar_rally_pct > 5: score += 10
        if ar_rally_pct > 10: score += 10
        if st_valid: score += 20
        if spring: score += 15
        if sos_valid: score += 20

        return {
            "type": "ACCUMULATION",
            "direction": "LONG",
            "SC_price": sc_price,
            "AR_high": ar_high,
            "ST_low": st_low,
            "spring_detected": spring,
            "SOS_detected": sos_valid,
            "range_high": ar_high,
            "range_low": min(sc_price, st_low),
        }, min(score, 97)

    def detect_distribution(self, df):
        """Detect Wyckoff Distribution pattern."""
        df = self.compute_features(df)
        if len(df) < 25:
            return None, 0

        segment = df.tail(40).copy()

        # 1. Buying Climax (BC): high volume, wide spread up
        bc_candidates = segment[segment["Volume_Spike"] &
                                 (segment["Close"] > segment["Close"].shift(1))].tail(5)
        if len(bc_candidates) == 0:
            return None, 0

        bc_idx = bc_candidates.index[-1]
        bc_loc = segment.index.get_loc(bc_idx)
        if bc_loc >= len(segment) - 2:
            return None, 0

        bc_price = segment.loc[bc_idx, "High"]
        bc_vol = segment.loc[bc_idx, "Volume"]

        # 2. Automatic Reaction (AR down)
        ar_segment = segment.iloc[bc_loc+1:]
        if len(ar_segment) < 3:
            return None, 0
        ar_low = ar_segment["Low"].min()

        # 3. Sign of Weakness (SOW)
        sow_segment = ar_segment.tail(10)
        sow = sow_segment[sow_segment["Low"] < ar_low].head(1)
        sow_valid = len(sow) > 0

        # Score
        score = 0
        score += 25  # BC
        if sow_valid: score += 25
        if len(segment) > 30 and segment["High"].iloc[-1] < bc_price * 0.98: score += 20
        if segment["Volume"].iloc[-3:].mean() < bc_vol * 0.6: score += 15

        if score < 40:
            return None, 0

        return {
            "type": "DISTRIBUTION",
            "direction": "SHORT",
            "BC_high": bc_price,
            "AR_low": ar_low,
            "SOW_detected": sow_valid,
            "range_high": bc_price,
            "range_low": ar_low,
        }, min(score, 97)

    def _atr(self, df, period):
        high, low, close = df["High"], df["Low"], df["Close"]
        tr = pd.concat([high - low,
                        (high - close.shift()).abs(),
                        (low - close.shift()).abs()], axis=1).max(axis=1)
        return tr.rolling(period).mean()

    def analyze(self, df):
        """Run both accumulation and distribution detection."""
        acc, acc_conf = self.detect_accumulation(df)
        dist, dist_conf = self.detect_distribution(df)
        signals = []
        if acc and acc_conf >= 50:
            acc["confidence"] = acc_conf
            signals.append(acc)
        if dist and dist_conf >= 50:
            dist["confidence"] = dist_conf
            signals.append(dist)
        return signals