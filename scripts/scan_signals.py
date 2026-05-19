"""Signal Scanner — runs all 22 strategies across multiple timeframes on watchlist + CMC top/trending"""
import sys, json, os
sys.path.insert(0, "/workspace/trading-bot")

from datetime import datetime
import config.settings as cfg
from exchange.data_fetcher import fetch_top_gainers, fetch_trending, fetch_current_price, fetch_global_data
from strategies.engine import StrategyEngine

def run(quick=False, timeframes=None, min_conf=50):
    print("=" * 60)
    print("🧠 AGIASE TRADING BOT — MULTI-THEORY SIGNAL SCAN")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    engine = StrategyEngine()
    if timeframes is None:
        timeframes = ["1h", "4h", "1d"]

    # 1. Market overview
    print("\n🌍 GLOBAL MARKET:")
    try:
        g = fetch_global_data()
        btc = g.get("bitcoin", {})
        eth = g.get("ethereum", {})
        btc_p = btc.get("usd", "?")
        btc_c = btc.get("usd_24h_change")
        eth_p = eth.get("usd", "?")
        eth_c = eth.get("usd_24h_change")
        total_mcap = g.get("total_market_cap", {}).get("usd", 0) / 1e12
        btc_dom = g.get("market_cap_percentage", {}).get("btc", 0)
        print(f"  BTC: ${btc_p:>6}  {f'{btc_c:+.2f}%' if btc_c else ''}")
        print(f"  ETH: ${eth_p:>6}  {f'{eth_c:+.2f}%' if eth_c else ''}")
        print(f"  Mkt Cap: ${total_mcap:.2f}T  |  BTC Dom: {btc_dom:.1f}%")
    except Exception as e:
        print(f"  ❌ Global error: {e}")

    # 2. Trending
    print("\n🔥 TRENDING (CoinGecko):")
    try:
        trending = fetch_trending()
        for i, c in enumerate(trending[:7], 1):
            rank = f" (#{c['market_cap_rank']})" if c.get('market_cap_rank') else ""
            print(f"  {i}. {c['name']} ({c['symbol']}){rank}")
    except Exception as e:
        print(f"  ❌ Trending: {e}")

    # 3. Top Gainers
    print("\n📈 TOP GAINERS (24h):")
    try:
        gainers = fetch_top_gainers(10)
        for i, c in enumerate(gainers[:5], 1):
            print(f"  {i}. {c['name']} ({c['symbol']}): ${c['price']:.4f} | {c['change_24h']:+.2f}%")
    except Exception as e:
        print(f"  ❌ Gainers: {e}")

    # 4. Signals — pick coins to scan
    if quick:
        scan_coins = cfg.QUICK_WATCHLIST
    else:
        scan_coins = cfg.WATCHLIST

    print(f"\n📊 SIGNALS ({len(scan_coins)} coins, {len(timeframes)}x TF, 22 strategies):")
    print(f"   Timeframes: {', '.join(timeframes)}")

    all_signals = []
    for coin_id in scan_coins:
        try:
            sym = coin_id[:4].upper()
            sigs = engine.analyze_ticker(coin_id, sym, timeframes=timeframes)
            all_signals.extend(sigs)
        except Exception as e:
            print(f"  ⚠️  {coin_id}: {e}")

    # Rank & display
    all_signals.sort(key=lambda s: s.get("confidence", 0), reverse=True)

    # Group by coin for per-coin summary
    from collections import defaultdict
    by_coin = defaultdict(list)
    for s in all_signals:
        by_coin[s["coin_id"]].append(s)

    for coin_id, sigs in by_coin.items():
        high_conf = [s for s in sigs if s.get("confidence", 0) >= min_conf]
        if not high_conf:
            continue
        print(f"\n  {coin_id.upper()} — {len(high_conf)} high-signals:")
        for s in high_conf[:5]:  # top 5 per coin
            d = "🟢" if s.get("direction") == "LONG" else "🔴"
            tf = s.get("timeframe", "1h")
            strat = s.get("strategy", "?").split("_", 1)[-1]
            conf = s.get("confidence", 0)
            print(f"    {d} [{tf}] {strat:<18} {s['direction']:<6} conf={conf:.0f}")

    # 5. Summary stats
    total_high = len([s for s in all_signals if s.get("confidence", 0) >= min_conf])
    longs = len([s for s in all_signals if s.get("direction") == "LONG" and s.get("confidence", 0) >= min_conf])
    shorts = len([s for s in all_signals if s.get("direction") == "SHORT" and s.get("confidence", 0) >= min_conf])
    print(f"\n  📊 TOTAAL: {total_high} high-signals | 🟢 {longs} LONG | 🔴 {shorts} SHORT")

    print("\n" + "=" * 60)
    return all_signals

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Only scan QUICK_WATCHLIST")
    parser.add_argument("--tf", nargs="+", default=["1h", "4h", "1d"], help="Timeframes to scan")
    parser.add_argument("--min-conf", type=float, default=50, help="Min confidence to show")
    args = parser.parse_args()
    run(quick=args.quick, timeframes=args.tf, min_conf=args.min_conf)