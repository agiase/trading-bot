"""
Hyperliquid Exchange Executor — trade execution via ccxt (USDC pairs)
"""
import ccxt
import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "wallet.json")

class HyperliquidExecutor:
    def __init__(self, testnet=False, wallet_address="", private_key=""):
        self.testnet = testnet
        wallet_addr = wallet_address
        is_testnet = testnet

        # Load from config file if not explicitly passed
        if not wallet_addr:
            try:
                with open(CONFIG_PATH) as f:
                    cfg = json.load(f)
                wallet_addr = cfg.get("hyperliquid", {}).get("address", "")
                is_testnet = cfg.get("hyperliquid", {}).get("testnet", False)
            except:
                pass

        self.exchange = ccxt.hyperliquid({
            "enableRateLimit": True,
            "walletAddress": wallet_addr,
            "privateKey": private_key,
        })

        if is_testnet:
            self.exchange.set_sandbox_mode(True)
        elif wallet_addr:
            self.exchange.headers = {"X-Wallet-Address": wallet_addr}
            if private_key:
                self.exchange.privateKey = private_key

        self.authenticated = bool(wallet_addr)
        self._markets_cache = None

    def _get_markets(self):
        if self._markets_cache is None:
            self.exchange.load_markets()
            self._markets_cache = self.exchange.markets
        return self._markets_cache

    def _resolve_symbol(self, ticker):
        """Convert BTC -> BTC/USDC, etc."""
        ticker = ticker.upper().replace("/", "")
        markets = self._get_markets()
        candidates = [s for s in markets if s.startswith(ticker + "/")]
        if not candidates:
            sym = f"{ticker}/USDC"
            if sym in markets:
                return sym
            raise ValueError(f"No market found for {ticker}. Available: {candidates[:5]}")
        return candidates[0]

    def check_connection(self):
        try:
            self.exchange.fetch_balance()
            return True
        except Exception as e:
            return {"error": str(e), "auth": self.authenticated}

    def get_balance(self):
        try:
            bal = self.exchange.fetch_balance()
            return bal.get("total", {})
        except Exception as e:
            return {"error": str(e)}

    def fetch_ticker(self, ticker):
        try:
            symbol = self._resolve_symbol(ticker)
            t = self.exchange.fetch_ticker(symbol)
            return {
                "symbol": symbol,
                "last": t["last"],
                "bid": t.get("bid"),
                "ask": t.get("ask"),
                "change_24h": t.get("percentage"),
                "volume": t.get("quoteVolume"),
                "high": t.get("high"),
                "low": t.get("low"),
            }
        except Exception as e:
            return {"error": str(e)}

    def fetch_ohlcv(self, ticker, timeframe="1m", limit=100):
        """Fetch OHLCV candles. Supported: 15s, 30s, 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 1d"""
        try:
            symbol = self._resolve_symbol(ticker)
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            return [{
                "timestamp": o[0],
                "open": o[1],
                "high": o[2],
                "low": o[3],
                "close": o[4],
                "volume": o[5],
            } for o in ohlcv]
        except Exception as e:
            return {"error": str(e)}

    def execute_signal(self, signal, ticker, size_usd=100):
        if not self.authenticated:
            return {"error": "Wallet not configured", "signal": signal}

        side = "buy" if signal.get("direction") == "LONG" else "sell"
        try:
            symbol = self._resolve_symbol(ticker)
            ticker_data = self.exchange.fetch_ticker(symbol)
            price = ticker_data["last"]
            amount = size_usd / price

            order = self.exchange.create_market_order(
                symbol=symbol,
                type="market",
                side=side,
                amount=amount,
            )

            return {
                "status": "executed",
                "side": side,
                "symbol": symbol,
                "size": round(amount, 4),
                "estimated_price": price,
                "confidence": signal.get("confidence"),
                "strategy": signal.get("strategy"),
                "order": order,
                "sl": signal.get("sl"),
                "tp": signal.get("tp"),
            }
        except Exception as e:
            return {"error": str(e), "signal": signal}
