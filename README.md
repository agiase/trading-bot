# 🤖 Agiase Trading Bot

Multi-strategy crypto trading bot met Wyckoff-analyse, CoinGecko data, en Hyperliquid executie.

## Structuur
```
trading-bot/
├── config/           # Instellingen & watchlist
├── exchange/         # Data fetchers & order executie
├── strategies/       # Trading strategieën (Wyckoff, ..)
├── learning/         # Trade history & trading theories
├── scripts/          # Scan & entry point
└── tests/
```

## Gebruik
```bash
cd /workspace/trading-bot
python3 scripts/scan_signals.py
```

## Strategieën
- **Wyckoff** — accumulation/distribution detectie ✅
- 22 trading theorieën opgeslagen in `learning/theories/`

## Exchange
- Hyperliquid (testnet/mainnet via ccxt)
- Wallet configuratie via `.env` of environment variables

## GitHub
https://github.com/agiase/trading-bot
