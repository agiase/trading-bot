"""Agiase Trading Bot — Global Configuration"""
import os, json
from dotenv import load_dotenv

load_dotenv()

# --- Exchange ---
EXCHANGE = os.getenv("EXCHANGE", "hyperliquid")
HYPERLIQUID_TESTNET = os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"
HYPERLIQUID_WALLET = os.getenv("HYPERLIQUID_WALLET", "0x9AAF25F116C9C19866E22136Afd902D00D171fFC")
HYPERLIQUID_PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY", "")

# --- Trading ---
MAX_POSITION_SIZE_USD = float(os.getenv("MAX_POSITION_SIZE_USD", "100"))
DEFAULT_LEVERAGE = int(os.getenv("DEFAULT_LEVERAGE", "3"))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "50.0"))
MAX_CONCURRENT_POSITIONS = int(os.getenv("MAX_CONCURRENT_POSITIONS", "3"))
AUTO_TRADE = os.getenv("AUTO_TRADE", "false").lower() == "true"
ASK_BEFORE_TRADE = os.getenv("ASK_BEFORE_TRADE", "true").lower() != "false"

# --- Risk ---
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "2.0"))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "6.0"))
MAX_DRAWDOWN_PCT = float(os.getenv("MAX_DRAWDOWN_PCT", "15.0"))

# --- Data ---
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Multi-timeframe config
TIMEFRAMES = {
    "scalp_30s":  {"ccxt": None, "cg_days": 1,   "label": "30s", "bars": 120},
    "scalp_1m":   {"ccxt": "1m",  "cg_days": 1,   "label": "1m",  "bars": 120},
    "scalp_5m":   {"ccxt": "5m",  "cg_days": 1,   "label": "5m",  "bars": 168},
    "short_15m":  {"ccxt": "15m", "cg_days": 1,   "label": "15m", "bars": 336},
    "short_1h":   {"ccxt": "1h",  "cg_days": 7,   "label": "1h",  "bars": 336},
    "medium_4h":  {"ccxt": "4h",  "cg_days": 14,  "label": "4h",  "bars": 168},
    "daily_1d":   {"ccxt": "1d",  "cg_days": 30,  "label": "1d",  "bars": 90},
    "weekly":     {"ccxt": "1w",  "cg_days": 365, "label": "1w",  "bars": 52},
}

DEFAULT_TIMEFRAMES = ["1h", "4h", "1d"]
OHLC_DAYS = 14

# --- Signals ---
SIGNAL_INTERVAL_HOURS = int(os.getenv("SIGNAL_INTERVAL_HOURS", "6"))

# --- Watchlist ---
def _load_watchlist():
    wl_path = os.path.join(os.path.dirname(__file__), "watchlist.json")
    try:
        with open(wl_path) as f:
            data = json.load(f)
        primary = [c["id"] for c in data.get("primary", [])]
        cmc = [c["id"] for c in data.get("cmc_watchlist", [])]
        broad = [c["id"] for c in data.get("broad", [])]
        all_ids = list(dict.fromkeys(primary + cmc + broad))  # dedup, preserve order
        return all_ids
    except:
        return ["bitcoin", "ethereum", "monero", "ripple"]

WATCHLIST = _load_watchlist()

# Short list for quick scans (top priority)
QUICK_WATCHLIST = ["bitcoin", "ethereum", "ripple", "solana", "monero", "bitcoin-cash-sv", "toncoin", "sui"]