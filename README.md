## Binance Trading Bot
A Python-based trading bot for Binance Futures Testnet.

## Setup
1. Activate virtual environment: `env\Scripts\activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python trading_bot.py --api-key YOUR_KEY --api-secret YOUR_SECRET --testnet True --symbol BTCUSDT --order-type market --side BUY --quantity 0.001`

## Features
- Market, limit, and stop-limit orders.
- Logging to `trading_bot.log`.
- Input validation and error handling.