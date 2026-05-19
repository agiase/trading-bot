"""
Signal Scanner — main entry point that runs all scans
"""
import sys
import json
sys.path.insert(0, "/workspace/trading-bot")

import config.settings as cfg
from exchange.data_fetcher import (
    fetch_top_gainers, fetch_trending, fetch_current_price, fetch_global_data,
    fetch_ohlcv, symbol_for, has_exchange_data
)
from strategies.engine import StrategyEngine

def run():
    print("=" * 55)
    print("🧠 AGIASE TRADING BOT — SIGNAL SCAN")
    print(f"   {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 55)

    # 1. Top Gainers
    print("\n🔥 TOP GAINERS (24h):")
    try:
        gainers = fetch_top_gainers(10)
        for i, c in enumerate(gainers[:5], 1):
            print(f"  {i}. {c['name']} ({c['symbol']}): ${c['price']:.4f} | {c['change_24h']:+.2f}%")
    except Exception as e:
        print(f"  ❌ CoinGecko error: {e}")

    # 2. Trending
    print("\n🔥 TRENDING:")
    try:
        trending = fetch_trending()
        for i, c in enumerate(trending[:5], 1):
            print(f"  {i}. {c['name']} ({c['symbol']})")
    except Exception as e:
        print(f"  ❌ Trending error: {e}")

    # 3. Watchlist Prices
    print("\n👁️  WATCHLIST PRICES:")
    watchlist_ids = cfg.WATCHLIST
    for coin_id in watchlist_ids:
        try:
            data = fetch_current_price(coin_id)
            if coin_id in data:
                d = data[coin_id]
                price = d.get("usd", "?")
                change = d.get("usd_24h_change")
                if change:
                    chg_str = f"{change:+.2f}%"
                else:
                    chg_str = "?"
                print(f"  {coin_id:<15} ${price:<8} {chg_str}")
        except:
            pass

    # 4. Strategy Signals (Wyckoff)
    print("\n📊 WYCKOFF SIGNALS:")
    engine = StrategyEngine()
    for coin_id in watchlist_ids:
        try:
            sym = symbol_for(coin_id)
            sigs = engine.analyze_ticker(coin_id, coin_id[:4], exchange_symbol=sym, days=14)
            for s in sigs:
                conf = s.get("confidence", 0)
                if conf >= 50:
                    dir_icon = "🟢" if s.get("direction") == "LONG" else "🔴"
                    rh = s.get("range_high", 0)
                    rl = s.get("range_low", 0)
                    print(f"  {dir_icon} {coin_id:<15} {s['direction']:<6} conf={conf:.0f}  range=${rl:.2f}–${rh:.2f}")
        except Exception as e:
            err = str(e)
            if "429" not in err and "400" not in err:
                print(f"  ⚠️  {coin_id}: {err}")

    # 5. Global Data
    print("\n🌍 GLOBAL MARKET:")
    try:
        g = fetch_global_data()
        print(f"  BTC: ${g.get('bitcoin', {}).get('usd', '?'):>8}")
        print(f"  ETH: ${g.get('ethereum', {}).get('usd', '?'):>8}")
        print(f"  Mkt Cap: ${g.get('total_market_cap', {}).get('usd', 0)/1e12:.2f}T")
    except:
        pass

    print("\n" + "=" * 55)

if __name__ == "__main__":
    run()