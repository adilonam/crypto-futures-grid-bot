from pybit.unified_trading import HTTP
import os
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Grid trading parameters
GRID_SIZE = 10  # Number of grid levels
PRICE_INTERVAL = 0.01  # Percentage interval between grid levels
TRADE_QUANTITY = 100  # Quantity per trade

def place_grid_orders(session, base_price, side):
    for i in range(GRID_SIZE):
        price_level = base_price * (1 + PRICE_INTERVAL * i) if side == 'Sell' else base_price * (1 - PRICE_INTERVAL * i)
        order = session.place_order(
            category="linear",
            symbol="XRPUSDT",
            side=side,
            orderType="Limit",
            qty=TRADE_QUANTITY,
            price=str(price_level),
            timeInForce="PostOnly",
            isLeverage=0,
            orderFilter="Order"
        )
        print(f"Placed {side} order at {price_level}: {order}")

def main():
    # Retrieve API key and secret from environment variables
    api_key = os.getenv('BYBIT_API_KEY')
    api_secret = os.getenv('BYBIT_API_SECRET')
    
    if not api_key or not api_secret:
        print("Please set the BYBIT_API_KEY and BYBIT_API_SECRET in the .env file.")
        return
    
    session = HTTP(
        demo=True, 
        api_key=api_key,
        api_secret=api_secret,
    )

    while True:
        try:
            # Fetch the ticker information
            ticker = session.get_tickers(
                category="linear",
                symbol="XRPUSDT"
            )
            # Extract and print the price
            if ticker and 'result' in ticker and 'list' in ticker['result'] and len(ticker['result']['list']) > 0:
                current_price = float(ticker['result']['list'][0]['lastPrice'])
                print(f"Current XRPUSDT Price: {current_price}")

                # Place Buy and Sell orders in a grid
                place_grid_orders(session, current_price, 'Buy')
                place_grid_orders(session, current_price, 'Sell')
            
            # Wait for a specified interval before the next request (e.g., 2 seconds)
            time.sleep(10)
        
        except Exception as e:
            print(f"Error fetching price: {e}")
            break

if __name__ == "__main__":
    main()
