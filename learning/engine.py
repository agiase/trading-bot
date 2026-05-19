"""
Learning Engine — stores trade history, learns from outcomes
"""
import json
import os
import pandas as pd
import numpy as np

HISTORY_FILE = "/workspace/trading-bot/data/trade_history.json"

class LearningEngine:
    def __init__(self):
        self.history = self._load()

    def _load(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE) as f:
                return json.load(f)
        return {"trades": [], "stats": {}}

    def _save(self):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.history, f, indent=2)

    def record_trade(self, trade):
        """Record a trade signal and its outcome."""
        self.history["trades"].append({
            **trade,
            "timestamp": str(pd.Timestamp.now(tz="UTC")),
        })
        self._update_stats()
        self._save()

    def _update_stats(self):
        trades = self.history["trades"]
        if not trades:
            return
        df = pd.DataFrame(trades)

        stats = {}
        if "outcome" in df.columns:
            won = df[df["outcome"] == "win"]
            lost = df[df["outcome"] == "loss"]
            stats["total_trades"] = len(df)
            stats["wins"] = len(won)
            stats["losses"] = len(lost)
            stats["win_rate"] = round(len(won) / len(df) * 100, 1) if len(df) > 0 else 0

        self.history["stats"] = stats

    def get_stats(self):
        return self.history.get("stats", {})

    def suggest_optimization(self):
        """Analyze historical performance and suggest parameter changes."""
        trades = self.history["trades"]
        if len(trades) < 10:
            return "Nog niet genoeg data (<10 trades) voor optimalisatie."

        df = pd.DataFrame(trades)
        suggestions = []

        if "confidence" in df.columns and "outcome" in df.columns:
            # Check if low-confidence trades lose more
            low_conf = df[df["confidence"] < 70]
            if len(low_conf) > 0:
                low_win_rate = len(low_conf[low_conf["outcome"] == "win"]) / len(low_conf)
                if low_win_rate < 0.4:
                    suggestions.append("Verhoog MIN_CONFIDENCE naar 70 — lage conf trades presteren slecht.")

        return suggestions if suggestions else ["Parameters lijken goed."]