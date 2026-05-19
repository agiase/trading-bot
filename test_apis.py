"""Test all data sources"""
import requests, sys

results = {}

# CoinPaprika
try:
    r = requests.get("https://api.coinpaprika.com/v1/tickers?limit=10", timeout=10)
    results["CoinPaprika"] = "OK (%d, %d coins)" % (r.status_code, len(r.json()))
except Exception as e:
    results["CoinPaprika"] = "ERR: %s" % e

# DexScreener
try:
    r = requests.get("https://api.dexscreener.com/latest/dex/pairs?chain=ethereum", timeout=10)
    results["DexScreener"] = "OK (%d)" % r.status_code
except Exception as e:
    results["DexScreener"] = "ERR: %s" % e

# CryptoCompare
try:
    r = requests.get("https://min-api.cryptocompare.com/data/top/mktcapfull?limit=5&tsym=USD", timeout=10)
    data = r.json()
    results["CryptoCompare"] = "OK (%d, %d coins)" % (r.status_code, len(data.get("Data", [])))
except Exception as e:
    results["CryptoCompare"] = "ERR: %s" % e

# CoinGecko
try:
    r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=8)
    results["CoinGecko"] = "OK (%d) %s" % (r.status_code, r.text[:60])
except Exception as e:
    results["CoinGecko"] = "ERR: %s" % e

# Binance
try:
    import ccxt
    ex = ccxt.binance()
    t = ex.fetch_ticker("BTC/USDT")
    results["Binance"] = "OK (BTC $%.2f)" % t["last"]
except Exception as e:
    results["Binance"] = "ERR: %s" % e

for k, v in results.items():
    print("%s: %s" % (k, v))