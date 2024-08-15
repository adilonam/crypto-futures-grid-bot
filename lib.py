from pybit.unified_trading import HTTP
import os
import time
from dotenv import load_dotenv
import random
import string

# Load environment variables from the .env file
load_dotenv()




class GridBot():
    # Grid trading parameters
    GRID_SIZE = 5  # Number of grid levels
    PRICE_INTERVAL = 0.001  # Percentage interval between grid levels
    TRADE_QUANTITY = 100  # Quantity per trade
    LEVERAGE = 20
    #CRYPTO TO TRADE
    SYMBOL = "XRPUSDT"
    CATEGORY = "linear"
    
    session = None
    grid_levels = []
    tolerance=0.0001
    bot_id= None
    
    def __init__(self) -> None:
        self.bot_id = self.generate_random_string(5)
        # Retrieve API key and secret from environment variables
        api_key = os.getenv('BYBIT_API_KEY')
        api_secret = os.getenv('BYBIT_API_SECRET')
        
        if not api_key or not api_secret:
            print("Please set the BYBIT_API_KEY and BYBIT_API_SECRET in the .env file.")
            return
        self.session = HTTP(
        demo=True, 
        api_key=api_key,
        api_secret=api_secret,
        )
        try:
            self.session.set_leverage(
                category=self.CATEGORY,
                symbol=self.SYMBOL,
                buyLeverage=str(self.LEVERAGE),
                sellLeverage=str(self.LEVERAGE),
            )
        except Exception as e:
            # Handle the exception, for example:
            print(f"An error occurred while setting leverage: {e}")
            # You can also log the error or take other actions here
            
    def generate_random_string(self, length):
        # Choose from uppercase, lowercase letters, and digits
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))  
        
    def place_grid_orders(self, price):
        for i in range(self.GRID_SIZE):
            if (price <= self.grid_levels[i]*(1+self.tolerance) and price >= self.grid_levels[i]*(1-self.tolerance) ):
                #handle buy
                _buy_id = f"{self.bot_id}-buy-{i}"
                if not self.is_order_exists(_buy_id):
                    order = self.session.place_order(
                        category=self.CATEGORY,
                        symbol=self.SYMBOL,
                        side="Buy",
                        orderType="Market",
                        qty=self.TRADE_QUANTITY,
                        timeInForce="PostOnly",
                        orderLinkId=_buy_id,
                        isLeverage=self.LEVERAGE,
                        orderFilter="Order",
                        positionIdx = 1,
                    )
                    print(f"Placed buy ", order)
                #handle sell
                _sell_id = f"{self.bot_id}-sell-{i}"
                if not self.is_order_exists(_sell_id):
                    order = self.session.place_order(
                        category=self.CATEGORY,
                        symbol=self.SYMBOL,
                        side="Sell",
                        orderType="Market",
                        qty=self.TRADE_QUANTITY,
                        timeInForce="PostOnly",
                        orderLinkId=_sell_id,
                        isLeverage=self.LEVERAGE,
                        orderFilter="Order",
                        positionIdx = 2,
                    )
                    print(f"Placed sell ", order)
                
    
    
    def get_last_price(self):
        try:
            # Fetch the ticker information
            ticker = self.session.get_tickers(
                category=self.CATEGORY,
                symbol=self.SYMBOL
            )
            # Extract and print the price
            if ticker and 'result' in ticker and 'list' in ticker['result'] and len(ticker['result']['list']) > 0:
                current_price = float(ticker['result']['list'][0]['lastPrice'])
                
            return current_price
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    def get_grid_levels(self, price):    
        if not self.grid_levels:
            for i in range(self.GRID_SIZE):
                price_level = price * (1 - self.PRICE_INTERVAL * int(self.GRID_SIZE/2) + self.PRICE_INTERVAL*i)
                self.grid_levels.append(price_level)
    
    def is_order_exists(self, orderLinkId):
        response = self.session.get_order_history(
        orderLinkId = orderLinkId,
        category=self.CATEGORY,
        symbol=self.SYMBOL,
    )   
        print("check order", orderLinkId)
        return (response["result"]["list"] != [])     
    def start(self):
        while True:
            print("---------------------------------------------------")
            print("---------------------------------------------------")
            price = self.get_last_price()
            print(f"Current XRPUSDT Price: {price}")
            
            self.get_grid_levels(price)
            print("gird levels:", self.grid_levels)
            print('id of bot:', self.bot_id)
            
            
            self.place_grid_orders(price)
            

            
            
            time.sleep(2)
    

    
    