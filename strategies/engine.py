"""
Multi-Strategy Engine — runs ALL 22 strategies and combines signals
"""
from strategies.wyckoff import WyckoffDetector
from strategies.dow import DowDetector
from strategies.elliott_wave import ElliottWaveDetector
from strategies.gann import GannDetector
from strategies.market_profile import MarketProfileDetector
from strategies.order_flow import OrderFlowDetector
from strategies.vsa import VSADetector
from strategies.smc import SMCDetector
from strategies.harmonic import HarmonicDetector
from strategies.supply_demand import SupplyDemandDetector
from strategies.algo_ml import MLDetector
from strategies.liquidity import LiquidityDetector
from strategies.level2 import Level2Detector
from strategies.auction_market import AuctionMarketDetector
from strategies.intermarket import IntermarketDetector
from strategies.onchain import OnChainDetector
from strategies.cyclic import CyclicDetector
from strategies.stat_arb import StatArbDetector
from strategies.sentiment import SentimentDetector
from strategies.orderblock import InstitutionalOBDetector
from strategies.renko import RenkoDetector
from strategies.momentum_meanrev import MomentumMeanRevDetector
from exchange.data_fetcher import fetch_ohlcv, symbol_for, has_exchange_data

class StrategyEngine:
    def __init__(self):
        self.strategies = {
            "1_wyckoff": WyckoffDetector().analyze,
            "2_dow": DowDetector().analyze,
            "3_elliott_wave": ElliottWaveDetector().analyze,
            "4_gann": GannDetector().analyze,
            "5_market_profile": MarketProfileDetector().analyze,
            "6_order_flow": OrderFlowDetector().analyze,
            "7_vsa": VSADetector().analyze,
            "8_smc": SMCDetector().analyze,
            "9_harmonic": HarmonicDetector().analyze,
            "10_supply_demand": SupplyDemandDetector().analyze,
            "11_algo_ml": MLDetector().analyze,
            "12_liquidity": LiquidityDetector().analyze,
            "13_level2": Level2Detector().analyze,
            "14_auction_market": AuctionMarketDetector().analyze,
            "15_intermarket": IntermarketDetector().analyze,
            "16_onchain": OnChainDetector().analyze,
            "17_cyclic": CyclicDetector().analyze,
            "18_stat_arb": StatArbDetector().analyze,
            "19_sentiment": SentimentDetector().analyze,
            "20_orderblock": InstitutionalOBDetector().analyze,
            "21_renko": RenkoDetector().analyze,
            "22_momentum_meanrev": MomentumMeanRevDetector().analyze,
        }

    def analyze_ticker(self, coin_id, symbol, exchange_symbol=None, days=14):
        """Run ALL 22 strategies on one ticker."""
        if exchange_symbol is None:
            exchange_symbol = symbol_for(coin_id)

        df = fetch_ohlcv(coin_id, symbol=exchange_symbol, limit=336, timeframe="1h")
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

    def scan_watchlist(self, watchlist_ids, days=14):
        """Scan whole watchlist with ALL 22 strategies and return ranked signals."""
        all_signals = []
        for item in watchlist_ids:
            coin_id = item["id"] if isinstance(item, dict) else item
            symbol = item.get("symbol", coin_id[:4]) if isinstance(item, dict) else coin_id[:4]
            sigs = self.analyze_ticker(coin_id, symbol, days=days)
            all_signals.extend(sigs)
        all_signals.sort(key=lambda s: s.get("confidence", 0), reverse=True)
        return all_signals