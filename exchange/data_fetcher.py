"""Data fetcher — multi-timeframe OHLCV from Binance ccxt + CoinGecko fallback"""
import ccxt
import pandas as pd
import numpy as np
import time, requests
from datetime import datetime, timezone

EXCHANGE = ccxt.binance()

# CoinGecko ID -> ccxt symbol mapping (expanded for CMC watchlist)
COINGECKO_TO_SYMBOL = {
    "bitcoin":           "BTC/USDT",
    "ethereum":          "ETH/USDT",
    "ripple":            "XRP/USDT",
    "solana":            "SOL/USDT",
    "bitcoin-cash":      "BCH/USDT",
    "monero":            "XMR/USDT",
    "toncoin":           "TON/USDT",
    "sui":               "SUI/USDT",
    "bittensor":         None,  # TAO not on Binance
    "ecash":             None,  # XEC not on Binance
    "qubic":             None,
    "zigcoin":           None,
    "bitcoin-cash-sv":   "BSV/USDT",
    "grin":              None,
    "litecoin":          "LTC/USDT",
    "polkadot":          "DOT/USDT",
    "chainlink":         "LINK/USDT",
    "zcash":             "ZEC/USDT",
    "sky":               "SKY/USDT",
    "pi":                None,
    "hyperliquid":       None,
    "ondo-finance":      None,
    "bonfida":           None,
    "pudgy-penguins":    None,
    "the-open-network":  "TON/USDT",
}

def fetch_ohlcv(coin_id, symbol=None, timeframe="1h", limit=336):
    """Fetch OHLCV from exchange via ccxt. Falls back to CoinGecko for unsupported coins."""
    if symbol:
        try:
            candles = EXCHANGE.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(candles, columns=["timestamp", "Open", "High", "Low", "Close", "Volume"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df.set_index("timestamp", inplace=True)
            return df
        except Exception as e:
            print(f"  Exchange error for {symbol} ({timeframe}): {e}")

    return _fetch_coingecko_ohlcv(coin_id, days=_timeframe_to_days(timeframe))

def _timeframe_to_days(tf):
    mapping = {"1m": 1, "5m": 1, "15m": 1, "30m": 1, "1h": 7, "4h": 14, "1d": 30, "1w": 365}
    return mapping.get(tf, 14)

def _fetch_coingecko_ohlcv(coin_id, days=14):
    """Fallback: CoinGecko OHLC."""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {"vs_currency": "usd", "days": days}
    time.sleep(1)
    try:
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 429:
            print(f"  429 on {coin_id} (CG), waiting 10s...")
            time.sleep(10)
            r = requests.get(url, params=params, timeout=15)
        if r.status_code != 200:
            return None
        data = r.json()
        df = pd.DataFrame(data, columns=["timestamp", "Open", "High", "Low", "Close"])
        df["Volume"] = 0
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        return df
    except Exception as e:
        print(f"  CG OHLCV error for {coin_id}: {e}")
        return None

def fetch_multi_timeframe_ohlcv(coin_id, timeframes=None):
    """Fetch OHLCV for multiple timeframes at once. Returns {tf_name: df}."""
    if timeframes is None:
        from config.settings import DEFAULT_TIMEFRAMES
        timeframes = DEFAULT_TIMEFRAMES
    
    symbol = symbol_for(coin_id)
    result = {}
    for tf in timeframes:
        limit_map = {"1h": 336, "4h": 168, "1d": 90, "5m": 168, "15m": 336, "1m": 120}
        limit = limit_map.get(tf, 200)
        df = fetch_ohlcv(coin_id, symbol=symbol, timeframe=tf, limit=limit)
        if df is not None and len(df) > 20:
            result[tf] = df
    return result

# --- CoinGecko helpers ---

def fetch_current_price(coin_id, vs_currency="usd"):
    import requests
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": vs_currency, "include_24hr_change": "true"}
    time.sleep(0.5)
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 429:
        time.sleep(5)
        r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return {}
    return r.json()

def fetch_top_gainers(limit=10):
    import requests
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "volume_desc", "per_page": 250, "page": 1, "sparkline": "false"}
    time.sleep(0.5)
    r = requests.get(url, params=params, timeout=15)
    if r.status_code == 429:
        time.sleep(10)
        r = requests.get(url, params=params, timeout=15)
    if r.status_code != 200:
        return []
    coins = r.json()
    coins_sorted = sorted(coins, key=lambda c: c.get("price_change_percentage_24h", 0) or 0, reverse=True)
    return [{
        "id": c["id"], "symbol": c["symbol"].upper(), "name": c["name"],
        "price": c["current_price"],
        "change_24h": round(c.get("price_change_percentage_24h", 0) or 0, 2),
        "market_cap": c.get("market_cap"), "volume": c.get("total_volume"),
    } for c in coins_sorted[:limit]]

def fetch_trending():
    import requests
    time.sleep(0.5)
    r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
    if r.status_code == 429:
        time.sleep(10)
        r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
    if r.status_code != 200:
        return []
    data = r.json().get("coins", [])
    return [{"id": c["item"]["id"], "symbol": c["item"]["symbol"].upper(), "name": c["item"]["name"],
             "market_cap_rank": c["item"].get("market_cap_rank")} for c in data[:10]]

def fetch_global_data():
    time.sleep(0.5)
    r = requests.get("https://api.coingecko.com/api/v3/global", timeout=10)
    if r.status_code == 429:
        time.sleep(10)
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=10)
    if r.status_code != 200:
        return {}
    result = r.json().get("data", {})
    price_data = fetch_current_price("bitcoin,ethereum")
    return result | price_data

def symbol_for(coin_id):
    return COINGECKO_TO_SYMBOL.get(coin_id)

def has_exchange_data(coin_id):
    return COINGECKO_TO_SYMBOL.get(coin_id) is not None