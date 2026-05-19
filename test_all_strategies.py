"""Test all 22 strategies on BTC data."""
from strategies.engine import StrategyEngine
import json

engine = StrategyEngine()
print(f'Loaded {len(engine.strategies)} strategies:')
for k in engine.strategies:
    print(f'  {k}')

print('\n--- Testing BTC scan ---')
sigs = engine.analyze_ticker('bitcoin', 'BTC', exchange_symbol='BTC/USDT')
print(f'Total signals: {len(sigs)}')
high = [s for s in sigs if s.get('confidence', 0) >= 50]
print(f'High confidence (>=50): {len(high)}')
for s in high:
    print(f'  [{s["strategy"]}] {s["direction"]} conf={s["confidence"]} — {s["detail"]}')

# Summary by strategy
from collections import Counter
strat_counts = Counter(s['strategy'] for s in sigs)
print(f'\nSignals per strategy:')
for k, c in strat_counts.most_common():
    print(f'  {k}: {c}')