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
    GRID_SIZE = 5000  # Number of grid levels must be higher than 2
    GRID_TOP= 0.8
    GRID_BOTTOM = 0.4
    TRADE_TYPE = "Buy"
    TRADE_QUANTITY = 100  # Quantity per trade
    LEVERAGE = 20
    #CRYPTO TO TRADE
    SYMBOL = "XRPUSDT"
    CATEGORY = "linear"
    
    
    #for dev puposes
    session = None
    grid_levels = []
    tolerance=0.01
    bot_id= None
    orders = []
    current_level = None
    init = False
    
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
        if self.TRADE_TYPE == "Buy":
            self.POSITION_IDX = 1
        elif self.TRADE_TYPE == "Sell":
            self.POSITION_IDX = 2
        else:
            raise Exception("Postion type is incorrect : ", self.TRADE_TYPE)
        
            
    def generate_random_string(self, length):
        # Choose from uppercase, lowercase letters, and digits
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))  
        
    def place_grid_orders(self, price):
            zone_top = self.grid_levels[self.current_level + 1] if (self.current_level + 1) < self.GRID_SIZE else 10000
            zone_bottom = self.grid_levels[self.current_level - 1]  if (self.current_level + 1) >= 0 else 0
            print('zone top :', zone_top)
            print('zone bottm :', zone_bottom)
            if (price <= zone_bottom or price >= zone_top ):
                #handle buy
                
                _order_id = f"{self.bot_id}-{len(self.orders)}"

                order = self.session.place_order(
                    category=self.CATEGORY,
                    symbol=self.SYMBOL,
                    side=self.TRADE_TYPE,
                    orderType="Market",
                    qty=self.TRADE_QUANTITY,
                    timeInForce="PostOnly",
                    orderLinkId=_order_id,
                    orderFilter="Order",
                )
                
                print(f"Placed {self.TRADE_TYPE} ", order)
                    
              
                
                
    
    
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
    def set_grid_levels(self):    
        if not self.grid_levels:
            interval = (self.GRID_TOP-self.GRID_BOTTOM)/(self.GRID_SIZE-1)
            for i in range(self.GRID_SIZE):
                price_level = self.GRID_BOTTOM + interval*i
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
        print('id of bot:', self.bot_id)
        self.set_grid_levels()
        print("gird levels:", self.grid_levels)
        
        while True:
            print("---------------------------------------------------")
            print("---------------------------------------------------")
            
            price = self.get_last_price()
            
            print(f"Current XRPUSDT Price: {price}")
            
            
            if not self.init:
                self.current_level = min(range(len(self.grid_levels)), key=lambda i: abs(self.grid_levels[i] - price))
                self.init = True
                
            
            print("Current level index ", self.current_level)
            
            
            
            self.place_grid_orders(price)
   
           
            
            
            time.sleep(2)
    

    
    