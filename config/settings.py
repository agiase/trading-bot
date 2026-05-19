"""
Agiase Trading Bot — Global Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Exchange ---
EXCHANGE = os.getenv("EXCHANGE", "hyperliquid")
HYPERLIQUID_TESTNET = os.getenv("HYPERLIQUID_TESTNET", "true").lower() == "true"
HYPERLIQUID_WALLET = os.getenv("HYPERLIQUID_WALLET", "")
HYPERLIQUID_PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY", "")

# --- Trading ---
MAX_POSITION_SIZE_USD = float(os.getenv("MAX_POSITION_SIZE_USD", "100"))
DEFAULT_LEVERAGE = int(os.getenv("DEFAULT_LEVERAGE", "3"))
MIN_CONFIDENCE = float(os.getenv("MIN_CONFIDENCE", "60.0"))
MAX_CONCURRENT_POSITIONS = int(os.getenv("MAX_CONCURRENT_POSITIONS", "3"))
AUTO_TRADE = os.getenv("AUTO_TRADE", "false").lower() == "true"
ASK_BEFORE_TRADE = os.getenv("ASK_BEFORE_TRADE", "true").lower() != "false"

# --- Risk ---
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "2.0"))
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "6.0"))
MAX_DRAWDOWN_PCT = float(os.getenv("MAX_DRAWDOWN_PCT", "15.0"))

# --- Data ---
COINGECKO_API = "https://api.coingecko.com/api/v3"
DEFAULT_TIMEFRAMES = ["1h", "4h", "1d"]
DEFAULT_LIMIT = 200  # candles
OHLC_DAYS = 14  # Valid: 1, 7, 14, 30, 90, 180, 365, max

# --- Signals ---
SIGNAL_INTERVAL_HOURS = int(os.getenv("SIGNAL_INTERVAL_HOURS", "6"))

# --- Watchlist (CoinGecko IDs) ---
PRIMARY_WATCHLIST = [
    "monero",          # XMR
    "bitcoin-cash-sv", # BSV
    "ripple",          # XRP
    "grin",            # GRIN
]

BROAD_WATCHLIST = [
    "bitcoin",
    "ethereum",
    "hyperliquid",
    "solana",
    "zcash",
    "litecoin",
    "polkadot",
    "chainlink",
    "ondo-finance",
    "bonfida",
    "pudgy-penguins",
    "the-open-network",
]

WATCHLIST = PRIMARY_WATCHLIST + BROAD_WATCHLIST