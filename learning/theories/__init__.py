"""
Trading Theories Reference — all known trading methodologies
Collected for Agiase Trading Bot knowledge base
"""

THEORIES = {
    "1_wyckoff": {
        "name": "Wyckoff Method",
        "core": "Markets move in cycles of accumulation and distribution driven by 'Composite Operator' (smart money).",
        "phases": "Accumulation: SC→AR→ST→Spring→SOS→LPS. Distribution: BC→AR→SOW→LPSY→LOT.",
        "laws": ["Supply & Demand", "Cause & Effect", "Effort vs Result"],
        "indicators": ["Volume spread analysis", "Price swing structure"],
        "timeframes": "30m-1d",
        "implemented": True
    },
    "2_dow": {
        "name": "Dow Theory",
        "core": "Market prices discount everything. Trends have three movements (primary, secondary, minor). A trend is valid until confirmed by reversal signals.",
        "phases": "Accumulation → Public participation → Distribution",
        "laws": ["Price discounts everything", "Three trend types", "Trends confirmed by volume", "Trends persist until reversal"],
        "indicators": ["Swing highs/lows", "HH/HL for uptrend", "LH/LL for downtrend"],
        "timeframes": "1h-1W"
    },
    "3_elliott_wave": {
        "name": "Elliott Wave Theory",
        "core": "Markets move in 5 impulsive waves (direction) and 3 corrective waves (counter-trend). Waves subdivide fractally.",
        "phases": "Impulse: 1-2-3-4-5. Correction: A-B-C.",
        "rules": ["Wave 2 never retraces 100% of Wave 1", "Wave 3 is never shortest", "Wave 4 doesn't enter Wave 1 territory"],
        "fib_tools": ["0.382, 0.5, 0.618, 0.786, 1.272, 1.618"],
        "timeframes": "5m-1W",
        "complexity": "High"
    },
    "4_gann": {
        "name": "Gann Theory",
        "core": "Price and time are related. Key geometric angles (1x1, 2x1, 1x2) define support/resistance. Time cycles repeat.",
        "tools": ["Gann angles", "Square of 9", "Cardinal squares", "Time cycles"],
        "timeframes": "All",
        "complexity": "Very high"
    },
    "5_market_profile": {
        "name": "Market Profile (TPO)",
        "core": "Prints time-price opportunities in 30-min letters (TPOs). Shows value area, POC, and range structure.",
        "concepts": ["Value Area (VA)", "Point of Control (POC)", "Initial Balance (IB)", "Range Extension"],
        "patterns": ["Normal day", "Trend day", "Neutral day", "Non-trend day"],
        "timeframes": "30m-1d",
        "requires": "High-quality tick data"
    },
    "6_order_flow": {
        "name": "Order Flow / Tape Reading",
        "core": "Reads real-time bid/ask activity — CVD, delta, cumulative delta, imbalances, absorptions.",
        "tools": ["CVD", "Delta", "Cumulative Delta", "Bid/Ask imbalance", "Iceberg detection", "Absorption"],
        "timeframes": "1s-5m",
        "requires": "Level 2 data"
    },
    "7_vsa": {
        "name": "Volume Spread Analysis (VSA)",
        "core": "Extension of Wyckoff. Every bar tells a story via price spread, closing price, and volume relationship.",
        "signals": {
            "No demand": "Up bar, narrow spread, low volume",
            "Stopping volume": "Wide spread, high volume, small range (climax)",
            "Upthrust": "High test of supply area, fails",
            "Spring": "Low test of support, recovers"
        },
        "timeframes": "5m-1d"
    },
    "8_ict_smc": {
        "name": "ICT / Smart Money Concepts (SMC)",
        "core": "Price moves via liquidity sweeps (stop hunts), Fair Value Gaps (FVG), Order Blocks (OB), and Market Structure Shifts (MSS).",
        "concepts": ["Order Block", "Fair Value Gap (FVG)", "Liquidity sweep", "Displacement", "Market Structure Shift", "HTF bias", "Time & Price"],
        "timeframes": "15m-4h for entries, 1d for bias",
        "controversial": True
    },
    "9_harmonic": {
        "name": "Harmonic Patterns",
        "core": "Fibonacci-based geometric price patterns with specific ratios (XABCD structure).",
        "patterns": ["Gartley (0.618)", "Butterfly (1.272)", "Bat (0.886)", "Crab (1.618)", "Shark", "Cypher"],
        "requires": "Precise fib tool, D or XABCD",
        "timeframes": "15m-1d"
    },
    "10_supply_demand": {
        "name": "Supply & Demand Zones",
        "core": "Draw horizontal zones where institutions left large orders. Price returns to these zones (RBR, DBD).",
        "rules": ["Fresh zones > tested zones", "Drop base rally (DBR) = demand", "Rally base drop (RBD) = supply"],
        "timeframes": "5m-1d"
    },
    "11_algo_ml": {
        "name": "Algorithmic / ML Trading",
        "core": "Use statistics and machine learning to generate signals — mean reversion, momentum, pairs, ML classifiers.",
        "techniques": ["Mean reversion (z-score)", "Momentum (RSI, MACD)", "Pairs trading (cointegration)", "Random Forest / XGBoost", "LSTM time series"],
        "requires": "Clean data, feature engineering, backtesting"
    },
    "12_liquidity": {
        "name": "Liquidity Theory",
        "core": "Price hunts liquidity (stop losses above highs / below lows) before reversing. All moves target high-liquidity zones.",
        "concepts": ["Buy-side liquidity (BSL)", "Sell-side liquidity (SSL)", "Liquidity pool", "Equal highs/lows", "Inducement"],
        "timeframes": "5m-4h"
    },
    "13_level2": {
        "name": "Level 2 / Orderbook Trading",
        "core": "Read the limit order book — bid/ask walls, spoofing, icebergs, absorption at key levels.",
        "tools": ["Bid/Ask volume profile", "Book depth", "Spoof detection", "Iceberg detection"],
        "requires": "Orderbook data feed"
    },
    "14_auction_market": {
        "name": "Auction Market Theory (AMT)",
        "core": "Markets are auctions balancing buyers and sellers. Price moves to find where most trade occurs (value area).",
        "phases": ["Open → Exploration", "Range formation", "Trend (extreme exploration)", "Range again"],
        "related": ["Market Profile", "Volume Profile"]
    },
    "15_intermarket": {
        "name": "Intermarket Analysis",
        "core": "Correlations between asset classes = predictive signal. BTC correlates with DXY, gold, S&P, M2 money supply.",
        "pairs": ["BTC ↔ DXY (inverse)", "BTC ↔ Gold", "BTC ↔ S&P 500", "ETH ↔ BTC ratio", "DXY ↔ risk assets"],
        "timeframes": "1d-1W"
    },
    "16_onchain": {
        "name": "On-Chain Analysis",
        "core": "Read blockchain data for supply/demand signals — exchange flows, MVRV, SOPR, whale accumulations.",
        "metrics": ["MVRV Z-Score", "SOPR", "Exchange Netflow", "Reserve Risk", "NUPL", "Puell Multiple", "STH/LTH"],
        "timeframes": "1d-1W"
    },
    "17_cyclic": {
        "name": "Cyclic / Seasonal Analysis",
        "core": "Crypto markets follow halving cycles, seasonal patterns, and month-end / quarter-end effects.",
        "cycles": ["Halving cycle (4 years)", "Monthly seasonality", "Days of week", "Tax season effects"],
        "timeframes": "1d-1M"
    },
    "18_stat_arb": {
        "name": "Statistical Arbitrage / Pairs",
        "core": "Trade pairs where spread reverts to mean. Cointegrated pairs = hedge ratio → z-score → entry/exit.",
        "steps": ["Find cointegrated pairs", "Compute hedge ratio (OLS)", "Track spread z-score", "Entry when z > 2 or < -2"],
        "requires": "Multiple ticker data, backtesting"
    },
    "19_sentiment": {
        "name": "Sentiment Analysis",
        "core": "Extreme sentiment = contrarian signal. Fear & Greed Index, funding rates, put/call ratios, social volume.",
        "sources": ["Fear & Greed Index", "Funding rates", "Open interest changes", "Twitter/Reddit volume", "Google Trends"],
        "timeframes": "1h-1d"
    },
    "20_orderblock_institutional": {
        "name": "Order Block / Institutional Flow",
        "core": "Institutions leave footprints via large blocks. Combined with market structure shifts and FVG for entries.",
        "concepts": ["Bullish OB (last down candle before rally)", "Bearish OB (last up candle before drop)", "Breaker blocks", "Mitigation"],
        "timeframes": "15m-4h",
        "note": "Overlaps with ICT/SMC but predates it"
    },
    "21_renko": {
        "name": "Renko / Heikin-Ashi",
        "core": "Time-independent charts that filter noise. Renko uses fixed brick size. Heikin-Ashi smooths candles.",
        "use": "Trend identification, support/resistance on brick structure",
        "timeframes": "Brick size (not time)"
    },
    "22_momentum_meanrev": {
        "name": "Momentum & Mean Reversion Combo",
        "core": "Trading the cycle: momentum in direction of trend, mean reversion at extremes. RSI + Bollinger Bands + MACD.",
        "entry": "Momentum = RSI > 60 in uptrend. Mean reversion = RSI < 30 in uptrend (pullback entry).",
        "timeframes": "1h-1d"
    }
}