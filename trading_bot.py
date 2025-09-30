import argparse
import logging
from binance import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import sys

logging.basicConfig(
    filename='trading_bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Bot initialized with Testnet=%s", testnet)

    def validate_symbol(self, symbol):
        try:
            info = self.client.get_symbol_info(symbol)
            if info:
                self.logger.info("Symbol %s is valid", symbol)
                return True
            self.logger.error("Invalid symbol: %s", symbol)
            return False
        except BinanceAPIException as e:
            self.logger.error("Error validating symbol %s: %s", symbol, str(e))
            return False

    def place_market_order(self, symbol, side, quantity):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_MARKET,
                quantity=quantity
            )
            self.logger.info("Market order placed: %s", order)
            return order
        except BinanceAPIException as e:
            self.logger.error("Error placing market order: %s", str(e))
            raise

    def place_limit_order(self, symbol, side, quantity, price):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                price=price
            )
            self.logger.info("Limit order placed: %s", order)
            return order
        except BinanceAPIException as e:
            self.logger.error("Error placing limit order: %s", str(e))
            raise

    def place_stop_limit_order(self, symbol, side, quantity, stop_price, limit_price):
        try:
            order = self.client.create_order(
                symbol=symbol,
                side=side,
                type=ORDER_TYPE_STOP_LOSS_LIMIT,
                timeInForce=TIME_IN_FORCE_GTC,
                quantity=quantity,
                stopPrice=stop_price,
                price=limit_price
            )
            self.logger.info("Stop-Limit order placed: %s", order)
            return order
        except BinanceAPIException as e:
            self.logger.error("Error placing stop-limit order: %s", str(e))
            raise

    def get_order_details(self, symbol, order_id):
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            self.logger.info("Fetched order details: %s", order)
            return order
        except BinanceAPIException as e:
            self.logger.error("Error fetching order details: %s", str(e))
            raise

def print_order_details(order):
    print("\nOrder Details:")
    print(f"Order ID: {order.get('orderId')}")
    print(f"Symbol: {order.get('symbol')}")
    print(f"Side: {order.get('side')}")
    print(f"Type: {order.get('type')}")
    print(f"Quantity: {order.get('origQty')}")
    print(f"Price: {order.get('price', 'N/A')}")
    print(f"Stop Price: {order.get('stopPrice', 'N/A')}")
    print(f"Status: {order.get('status')}")
    print(f"Time: {order.get('time')}")

def main():
    parser = argparse.ArgumentParser(description="Binance Futures Trading Bot")
    parser.add_argument('--api-key', required=True, help="Binance API Key")
    parser.add_argument('--api-secret', required=True, help="Binance API Secret")
    parser.add_argument('--symbol', default="BTCUSDT", help="Trading pair (e.g., BTCUSDT)")
    parser.add_argument('--order-type', choices=['market', 'limit', 'stop-limit'], required=True, help="Order type")
    parser.add_argument('--side', choices=['BUY', 'SELL'], required=True, help="Order side")
    parser.add_argument('--quantity', type=float, required=True, help="Order quantity")
    parser.add_argument('--price', type=float, help="Limit order price (required for limit/stop-limit)")
    parser.add_argument('--stop-price', type=float, help="Stop price for stop-limit order")

    args = parser.parse_args()

    # Initialize bot
    bot = BasicBot(args.api_key, args.api_secret, testnet=True)

    # Validate symbol
    if not bot.validate_symbol(args.symbol):
        print(f"Error: Invalid symbol {args.symbol}")
        sys.exit(1)

    try:
        # Place order based on type
        if args.order_type == 'market':
            order = bot.place_market_order(args.symbol, args.side, args.quantity)
        elif args.order_type == 'limit':
            if args.price is None:
                print("Error: Price is required for limit orders")
                sys.exit(1)
            order = bot.place_limit_order(args.symbol, args.side, args.quantity, args.price)
        elif args.order_type == 'stop-limit':
            if args.price is None or args.stop_price is None:
                print("Error: Both price and stop-price are required for stop-limit orders")
                sys.exit(1)
            order = bot.place_stop_limit_order(args.symbol, args.side, args.quantity, args.stop_price, args.price)

        order_details = bot.get_order_details(args.symbol, order['orderId'])
        print_order_details(order_details)

        print("\nExecution successful. Check trading_bot.log for details.")

    except BinanceAPIException as e:
        print(f"API Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()