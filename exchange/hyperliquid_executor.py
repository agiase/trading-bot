"""
Hyperliquid Exchange Executor — trade execution via ccxt
"""
import ccxt

class HyperliquidExecutor:
    def __init__(self, testnet=True, wallet_address="", private_key=""):
        self.testnet = testnet
        self.exchange = ccxt.hyperliquid({
            "enableRateLimit": True,
        })
        if testnet:
            self.exchange.set_sandbox_mode(True)

        if wallet_address and private_key:
            self.exchange.private_key = private_key
            self.exchange.wallet_address = wallet_address
            self.authenticated = True
        else:
            self.authenticated = False

    def check_connection(self):
        """Check if exchange is reachable."""
        try:
            self.exchange.fetch_balance()
            return True
        except Exception as e:
            return {"error": str(e), "auth": self.authenticated}

    def get_balance(self):
        """Get wallet balance."""
        try:
            bal = self.exchange.fetch_balance()
            return bal.get("total", {})
        except Exception as e:
            return {"error": str(e)}

    def execute_signal(self, signal, ticker, size_usd=100):
        """Convert a signal into a market order."""
        if not self.authenticated:
            return {"error": "Wallet not configured", "signal": signal}

        side = "buy" if signal.get("direction") == "LONG" else "sell"
        symbol = f"{ticker.upper()}/USD"

        try:
            ticker_data = self.exchange.fetch_ticker(symbol)
            price = ticker_data["last"]
            amount = size_usd / price

            order = self.exchange.create_market_order(
                symbol=symbol,
                type="market",
                side=side,
                amount=amount,
            )

            result = {
                "status": "executed",
                "side": side,
                "symbol": symbol,
                "size": round(amount, 4),
                "estimated_price": price,
                "confidence": signal.get("confidence"),
                "strategy": signal.get("strategy"),
                "order": order,
            }

            # Add SL/TP if provided
            if signal.get("sl"):
                result["stop_loss"] = signal["sl"]
            if signal.get("tp"):
                result["take_profit"] = signal["tp"]

            return result

        except Exception as e:
            return {"error": str(e), "signal": signal}