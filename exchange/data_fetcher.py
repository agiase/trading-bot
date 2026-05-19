"""
Data fetcher — uses ccxt to fetch real OHLCV from exchanges (no rate limits, includes volume)
"""
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timezone

# CoinGecko -> exchange symbol mapping
EXCHANGE = ccxt.binance()  # Free, no API key needed for public data

# CoinGecko ID -> ccxt symbol mapping
COINGECKO_TO_SYMBOL = {
    # Primary watchlist
    "monero":           "XMR/USDT",
    "bitcoin-cash-sv":  "BSV/USDT",
    "ripple":           "XRP/USDT",
    "grin":             None,  # Not on Binance
    # Broad watchlist
    "bitcoin":          "BTC/USDT",
    "ethereum":         "ETH/USDT",
    "hyperliquid":      None,  # Not on Binance
    "solana":           "SOL/USDT",
    "zcash":            "ZEC/USDT",
    "litecoin":         "LTC/USDT",
    "polkadot":         "DOT/USDT",
    "chainlink":        "LINK/USDT",
    "ondo-finance":     None,  # Not on Binance
    "bonfida":          None,  # Not on Binance
    "pudgy-penguins":   None,  # Not on Binance
    "the-open-network": None,  # Not on Binance
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
            print(f"  Exchange error for {symbol}: {e}")

    # Fallback: try CoinGecko (no volume, limited)
    return _fetch_coingecko_ohlcv(coin_id)

def _fetch_coingecko_ohlcv(coin_id, days=14):
    """Fallback: CoinGecko OHLC (no volume column)."""
    import requests, time
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {"vs_currency": "usd", "days": days}
    r = requests.get(url, params=params, timeout=15)
    if r.status_code == 429:
        print(f"  429 on {coin_id} (CG), waiting 10s...")
        time.sleep(10)
        r = requests.get(url, params=params, timeout=15)
    if r.status_code != 200:
        return None
    data = r.json()
    # CoinGecko OHLC returns: [timestamp, open, high, low, close] — NO volume
    df = pd.DataFrame(data, columns=["timestamp", "Open", "High", "Low", "Close"])
    df["Volume"] = 0  # dummy volume
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    return df

# --- CoinGecko helpers for price/trending (these work fine) ---

def fetch_current_price(coin_id, vs_currency="usd"):
    """Fetch current price and 24h change from CoinGecko."""
    import requests, time
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": vs_currency,
              "include_24hr_change": "true"}
    time.sleep(0.5)
    r = requests.get(url, params=params, timeout=10)
    if r.status_code == 429:
        time.sleep(5)
        r = requests.get(url, params=params, timeout=10)
    if r.status_code != 200:
        return {}
    return r.json()

def fetch_top_gainers(limit=10):
    """Fetch top gainers via CoinGecko."""
    import requests, time
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {"vs_currency": "usd", "order": "volume_desc",
              "per_page": 250, "page": 1, "sparkline": "false"}
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
    import requests, time
    time.sleep(0.5)
    r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
    if r.status_code == 429:
        time.sleep(10)
        r = requests.get("https://api.coingecko.com/api/v3/search/trending", timeout=10)
    if r.status_code != 200:
        return []
    data = r.json().get("coins", [])
    return [{
        "id": c["item"]["id"],
        "symbol": c["item"]["symbol"].upper(),
        "name": c["item"]["name"],
        "market_cap_rank": c["item"].get("market_cap_rank"),
    } for c in data[:10]]

def fetch_global_data():
    """Fetch global market data."""
    import requests, time
    time.sleep(0.5)
    r = requests.get("https://api.coingecko.com/api/v3/global", timeout=10)
    if r.status_code == 429:
        time.sleep(10)
        r = requests.get("https://api.coingecko.com/api/v3/global", timeout=10)
    if r.status_code != 200:
        return {}
    return r.json().get("data", {})

# --- Symbol lookup ---
def symbol_for(coin_id):
    """Get ccxt symbol for a coin_id, or None."""
    return COINGECKO_TO_SYMBOL.get(coin_id)

def has_exchange_data(coin_id):
    """Check if we can fetch OHLCV with volume from exchange."""
    return COINGECKO_TO_SYMBOL.get(coin_id) is not None