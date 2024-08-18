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
    GRID_SIZE = 2500  # Number of grid levels must be higher than 2
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
    current_level_index = None
    init = False
    win = False
    interval = 0.01
    
    def __init__(self) -> None:
        self.bot_id = self.generate_random_string(5)
        self.interval = (self.GRID_TOP-self.GRID_BOTTOM)/(self.GRID_SIZE-1)
        self.set_grid_levels()
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
    
    def update_current_level_index(self, price):
        current_lvl_idx = min(range(len(self.grid_levels)), key=lambda i: abs(self.grid_levels[i] - price))
        if self.current_level_index:
            if((current_lvl_idx > self.current_level_index ) and self.TRADE_TYPE == "Buy" ) or  ((current_lvl_idx < self.current_level_index ) and self.TRADE_TYPE == "Sell" ):
                self.win = True
            else:
                self.win = False
        self.current_level_index = current_lvl_idx
        
    def place_grid_orders(self, price):
            if not self.init:
                self.update_current_level_index(price)
                self.init = True
            
            zone_top = self.grid_levels[self.current_level_index + 1] if (self.current_level_index + 1) < self.GRID_SIZE else 10000
            zone_bottom = self.grid_levels[self.current_level_index - 1]  if (self.current_level_index - 1) >= 0 else 0
            
            print('zone top :', zone_top)
            print('zone bottm :', zone_bottom)
            
            if (price <= zone_bottom or price >= zone_top ):
                #handle buy
                # Step 2: Check if there's an open Buy position
                
                _order_id = f"{self.bot_id}-{len(self.orders)}"
                try:
                    if self.TRADE_TYPE == "Buy":
                        tp = self.grid_levels[self.current_level_index + 2] if (self.current_level_index + 2) < self.GRID_SIZE else 10000
                        if(tp <= price):
                            tp = price + self.interval
                    else:
                        tp = self.grid_levels[self.current_level_index - 2]  if (self.current_level_index - 2) >= 0 else 0
                        if(tp >= price):
                            tp = price - self.interval
                    
                    order = self.session.place_order(
                        category=self.CATEGORY,
                        symbol=self.SYMBOL,
                        side=self.TRADE_TYPE,
                        orderType="Market",
                        qty=self.TRADE_QUANTITY,
                        orderLinkId=self.generate_random_string(5),
                    )
                    
                    
                    self.orders.append(_order_id)
                    self.update_current_level_index(price)
                    print("is win :",self.win)
                    print(f"Placed {self.TRADE_TYPE} order successfully: {order}")
                    
                    try:
                        self.session.set_trading_stop(
                            category=self.CATEGORY,
                            symbol=self.SYMBOL,
                            takeProfit=str(tp),
                            tpslMode="Partial",
                            tpSize=str(self.TRADE_QUANTITY),
                        )
                        print("Trading stop successfully set.")
                    except Exception as e:
                        print(f"An error occurred while setting the trading stop: {e}")

                except Exception as e:
                    print(f"Failed to place {self.TRADE_TYPE} order: {e}")
                
                

                
            
                
                
                    
              
                
                
    
    
    def get_last_price(self):
        try:
            # Fetch the ticker information
            ticker = self.session.get_tickers(
                category=self.CATEGORY,
                symbol=self.SYMBOL
            )
            current_price = None
            # Extract and print the price
            if ticker and 'result' in ticker and 'list' in ticker['result'] and len(ticker['result']['list']) > 0:
                current_price = float(ticker['result']['list'][0]['bid1Price'])
                
            return current_price
        except Exception as e:
            print(f"Error fetching price: {e}")
            return None
    def set_grid_levels(self):    
        if not self.grid_levels:
            
            for i in range(self.GRID_SIZE):
                price_level = self.GRID_BOTTOM + self.interval*i
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
       
        print("gird levels:", self.grid_levels)
        
        while True:
            print("---------------------------------------------------")
            print("---------------------------------------------------")
            
            price = self.get_last_price()
            
            print(f"Current XRPUSDT Price: {price}")
           
            
            self.place_grid_orders(price)
            print("Current level index ", self.current_level_index)
   
           
            
            
            time.sleep(2)
    

    
    