"""
CoinGecko data fetcher — multi-ticker, multi-timeframe with rate limiting
"""
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timezone

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
_last_call = 0

def _rate_limit(delay=1.5):
    """Ensure minimum delay between API calls."""
    global _last_call
    elapsed = time.time() - _last_call
    if elapsed < delay:
        time.sleep(delay - elapsed)
    _last_call = time.time()

def fetch_ohlcv(coin_id, vs_currency="usd", days=14):
    """Fetch OHLCV data from CoinGecko with rate limiting."""
    _rate_limit()
    url = f"{COINGECKO_BASE}/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs_currency, "days": days}
    r = requests.get(url, params=params, timeout=15)
    if r.status_code == 429:
        # CoinGecko rate limit exceeded; wait and retry once
        print(f"  429 on {coin_id}, waiting 5s...")
        time.sleep(5)
        r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df.columns = [c.capitalize() for c in df.columns]
    return df

def fetch_current_price(coin_id, vs_currency="usd"):
    """Fetch current price and 24h change."""
    _rate_limit()
    url = f"{COINGECKO_BASE}/simple/price"
    params = {"ids": coin_id, "vs_currencies": vs_currency,
              "include_24hr_change": "true", "include_market_cap": "true"}
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 429:
        time.sleep(5)
        r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_top_gainers(limit=10):
    """Fetch top gainers via /coins/markets sorted by 24h change."""
    _rate_limit()
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {"vs_currency": "usd", "order": "volume_desc",
              "per_page": 250, "page": 1, "sparkline": "false"}
    r = requests.get(url, params=params, timeout=15)
    if r.status_code == 429:
        time.sleep(5)
        r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    coins = r.json()
    coins_sorted = sorted(coins, key=lambda c: c.get("price_change_percentage_24h", 0) or 0, reverse=True)
    return [{
        "id": c["id"],
        "symbol": c["symbol"].upper(),
        "name": c["name"],
        "price": c["current_price"],
        "change_24h": round(c.get("price_change_percentage_24h", 0) or 0, 2),
        "market_cap": c.get("market_cap"),
        "volume": c.get("total_volume"),
    } for c in coins_sorted[:limit]]

def fetch_trending():
    """Fetch trending coins from CoinGecko."""
    _rate_limit()
    r = requests.get(f"{COINGECKO_BASE}/search/trending", timeout=10)
    if r.status_code == 429:
        time.sleep(5)
        r = requests.get(f"{COINGECKO_BASE}/search/trending", timeout=10)
    r.raise_for_status()
    data = r.json().get("coins", [])
    return [{
        "id": c["item"]["id"],
        "symbol": c["item"]["symbol"].upper(),
        "name": c["item"]["name"],
        "market_cap_rank": c["item"].get("market_cap_rank"),
        "price_btc": c["item"].get("price_btc"),
    } for c in data[:10]]

def fetch_global_data():
    """Fetch global market data."""
    _rate_limit()
    r = requests.get(f"{COINGECKO_BASE}/global", timeout=10)
    if r.status_code == 429:
        time.sleep(5)
        r = requests.get(f"{COINGECKO_BASE}/global", timeout=10)
    r.raise_for_status()
    return r.json()["data"]

if __name__ == "__main__":
    top = fetch_top_gainers(5)
    for c in top:
        print(f"{c['name']} ({c['symbol']}): ${c['price']:.4f} | {c['change_24h']:+.2f}%")