"""
Multi-Strategy Engine — runs all strategies and combines signals
"""
from strategies.wyckoff import WyckoffDetector
from exchange.data_fetcher import fetch_ohlcv

class StrategyEngine:
    def __init__(self):
        self.wyckoff = WyckoffDetector()
        self.strategies = {
            "wyckoff": self.wyckoff.analyze,
        }

    def analyze_ticker(self, coin_id, symbol, days=21):
        """Run all strategies on one ticker."""
        df = fetch_ohlcv(coin_id, days=days)
        if df is None or len(df) < 30:
            return []

        signals = []
        for name, func in self.strategies.items():
            try:
                sigs = func(df)
                for s in sigs:
                    s["strategy"] = name
                    s["coin_id"] = coin_id
                    s["symbol"] = symbol
                signals.extend(sigs)
            except Exception as e:
                print(f"  {name} error on {coin_id}: {e}")
        return signals

    def scan_watchlist(self, watchlist_ids, days=21):
        """Scan whole watchlist and return ranked signals."""
        all_signals = []
        for item in watchlist_ids:
            coin_id = item["id"] if isinstance(item, dict) else item
            symbol = item.get("symbol", coin_id[:4]) if isinstance(item, dict) else coin_id[:4]
            sigs = self.analyze_ticker(coin_id, symbol, days)
            all_signals.extend(sigs)
        # Sort by confidence descending
        all_signals.sort(key=lambda s: s.get("confidence", 0), reverse=True)
        return all_signals