import sys
sys.path.insert(0, '/workspace/trading-bot')
from exchange.hyperliquid_executor import HyperliquidExecutor
ex = HyperliquidExecutor(testnet=False)
ticker = ex.fetch_ticker('BTC')
print('BTC:', ticker)
