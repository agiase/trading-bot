import sys; sys.path.insert(0, '.')
from exchange.hyperliquid_executor import HyperliquidExecutor
ex = HyperliquidExecutor()
for tf in ['15s', '30s', '1m', '3m', '5m', '15m']:
    candles = ex.fetch_ohlcv('BTC', timeframe=tf, limit=3)
    if isinstance(candles, list) and len(candles) > 0:
        print(f'{tf}: last close={candles[-1]["close"]}, vol={candles[-1]["volume"]:.2f}')
    else:
        print(f'{tf}: {candles}')
