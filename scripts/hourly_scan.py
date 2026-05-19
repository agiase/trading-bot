"""Agiase Hourly Scan — top movers + 22 strategy signals"""
import sys, json, os, time
sys.path.insert(0, "/workspace/trading-bot")

from datetime import datetime
import requests
import config.settings as cfg
from exchange.data_fetcher import fetch_ohlcv, symbol_for
from strategies.engine import StrategyEngine

# ─── Fast data sources (no API key needed) ───────────────────────────────

def paprika_top_movers(limit=30):
    """CoinPaprika — fastest free top movers API"""
    r = requests.get("https://api.coinpaprika.com/v1/tickers?limit=%d" % limit, timeout=10)
    coins = r.json()
    for c in coins:
        c["change_24h"] = c.get("quotes", {}).get("USD", {}).get("percent_change_24h", 0)
        c["price"] = c.get("quotes", {}).get("USD", {}).get("price", 0)
        c["volume"] = c.get("quotes", {}).get("USD", {}).get("volume_24h", 0)
    gainers = sorted(coins, key=lambda c: c["change_24h"] or 0, reverse=True)
    losers = sorted(coins, key=lambda c: c["change_24h"] or 0)
    return gainers[:10], losers[:10]

def cryptocompare_top(limit=20):
    """CryptoCompare — top by market cap"""
    r = requests.get("https://min-api.cryptocompare.com/data/top/mktcapfull?limit=%d&tsym=USD" % limit, timeout=10)
    data = r.json().get("Data", [])
    result = []
    for item in data:
        c = item.get("CoinInfo", {})
        d = item.get("DISPLAY", {}).get("USD", {})
        rv = item.get("RAW", {}).get("USD", {})
        result.append({
            "id": c.get("Name", "").lower(),
            "symbol": c.get("Name", ""),
            "name": c.get("FullName", ""),
            "price": rv.get("PRICE", 0),
            "change_24h": rv.get("CHANGEPCT24HOUR", 0),
            "volume": rv.get("TOTALVOLUME24HTO", 0),
        })
    return result

def dexscreener_trending(chain="ethereum", limit=10):
    """DexScreener — trending pairs on a chain"""
    try:
        r = requests.get("https://api.dexscreener.com/latest/dex/pairs?chain=%s" % chain, timeout=8)
        pairs = r.json().get("pairs", [])
        pairs.sort(key=lambda p: float(p.get("volume", {}).get("h24", 0) or 0), reverse=True)
        result = []
        for p in pairs[:limit]:
            result.append({
                "symbol": p.get("baseToken", {}).get("symbol", ""),
                "name": p.get("baseToken", {}).get("name", ""),
                "price": float(p.get("priceUsd", 0) or 0),
                "change_24h": float(p.get("priceChange", {}).get("h24", 0) or 0),
                "volume": float(p.get("volume", {}).get("h24", 0) or 0),
                "liquidity": float(p.get("liquidity", {}).get("usd", 0) or 0),
                "chain": chain,
            })
        return result
    except:
        return []

# ─── Main scan ───────────────────────────────────────────────────────────

def run_scan():
    print("=" * 60)
    print("  AGIASE HOURLY SCAN")
    print("  %s" % datetime.now().strftime("%Y-%m-%d %H:%M UTC"))
    print("=" * 60)

    # 1. Top movers (CoinPaprika — fastest)
    print("\n[1/5] TOP GAINERS (24h) — CoinPaprika:")
    gainers, losers = paprika_top_movers(30)
    for i, c in enumerate(gainers[:5], 1):
        print("  %d. %s (%s): $%.4f | %+.2f%% | vol: $%.0f" % (
            i, c.get("name","?"), c.get("symbol","?"), c.get("price",0),
            c.get("change_24h",0), c.get("volume",0)))

    print("\n[2/5] TOP LOSERS (24h) — CoinPaprika:")
    for i, c in enumerate(losers[:5], 1):
        print("  %d. %s (%s): $%.4f | %.2f%% | vol: $%.0f" % (
            i, c.get("name","?"), c.get("symbol","?"), c.get("price",0),
            c.get("change_24h",0), c.get("volume",0)))

    # 2. CryptoCompare top market cap
    print("\n[3/5] TOP MARKET CAP — CryptoCompare:")
    cc_top = cryptocompare_top(15)
    for i, c in enumerate(cc_top[:5], 1):
        print("  %d. %s (%s): $%.2f | %+.2f%%" % (
            i, c["name"], c["symbol"], c["price"], c["change_24h"]))

    # 3. DexScreener — trending DEX pairs
    print("\n[4/5] DEX TRENDING — DexScreener:")
    for chain in ["ethereum", "solana", "bsc"]:
        pairs = dexscreener_trending(chain, 3)
        if pairs:
            print("  %s:" % chain.capitalize())
            for p in pairs:
                print("    %s: $%.6f | %+.2f%% | vol: $%.0f | liq: $%.0f" % (
                    p["symbol"], p["price"], p["change_24h"], p["volume"], p["liquidity"]))

    # 4. Strategy signals — pick top gainers + watchlist
    print("\n[5/5] STRATEGY SIGNALS (22 theories, 3x TF):")
    
    # Pick coins: top 5 gainers + top 5 losers + watchlist
    scan_ids = set()
    for c in gainers[:5]:
        scan_ids.add(c.get("id", "").lower())
    for c in losers[:5]:
        scan_ids.add(c.get("id", "").lower())
    for cid in cfg.QUICK_WATCHLIST:
        scan_ids.add(cid)
    
    scan_ids = list(scan_ids)[:15]  # max 15 coins
    timeframes = ["1h", "4h", "1d"]
    
    engine = StrategyEngine()
    all_signals = []
    
    for coin_id in scan_ids:
        sym = symbol_for(coin_id)
        if not sym:
            continue
        try:
            sigs = engine.analyze_ticker(coin_id, sym, timeframes=timeframes)
            all_signals.extend(sigs)
        except Exception as e:
            pass
    
    # Filter high confidence
    high = [s for s in all_signals if s.get("confidence", 0) >= 50]
    high.sort(key=lambda s: s.get("confidence", 0), reverse=True)
    
    from collections import defaultdict
    by_coin = defaultdict(list)
    for s in high:
        by_coin[s["coin_id"]].append(s)
    
    for coin_id, sigs in by_coin.items():
        print("\n  %s — %d signals:" % (coin_id.upper(), len(sigs)))
        for s in sigs[:3]:
            d = "LONG" if s.get("direction") == "LONG" else "SHORT"
            icon = "🟢" if s.get("direction") == "LONG" else "🔴"
            tf = s.get("timeframe", "1h")
            strat = s.get("strategy", "?").split("_", 1)[-1]
            conf = s.get("confidence", 0)
            print("    %s [%s] %-18s %-6s conf=%.0f" % (icon, tf, strat, d, conf))
    
    total_high = len(high)
    longs = len([s for s in high if s.get("direction") == "LONG"])
    shorts = len([s for s in high if s.get("direction") == "SHORT"])
    print("\n  TOTAAL: %d high-signals | LONG: %d | SHORT: %d" % (total_high, longs, shorts))
    
    # Save to file for reference
    report = {
        "timestamp": datetime.now().isoformat(),
        "gainers": [{"name": c.get("name"), "symbol": c.get("symbol"), "change": c.get("change_24h"), "price": c.get("price")} for c in gainers[:5]],
        "losers": [{"name": c.get("name"), "symbol": c.get("symbol"), "change": c.get("change_24h"), "price": c.get("price")} for c in losers[:5]],
        "signals": [{"coin": s["coin_id"], "strategy": s.get("strategy"), "direction": s.get("direction"), "timeframe": s.get("timeframe"), "confidence": s.get("confidence")} for s in high],
        "summary": {"total": total_high, "longs": longs, "shorts": shorts},
    }
    os.makedirs("/workspace/trading-bot/scans", exist_ok=True)
    with open("/workspace/trading-bot/scans/latest.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n  Report saved to scans/latest.json")

if __name__ == "__main__":
    run_scan()