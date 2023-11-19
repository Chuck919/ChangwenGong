from API import api_key, api_secret

from binance.client import Client
import time
import threading
from decimal import Decimal, ROUND_DOWN

#api_key = 'API Key'
#api_secret = 'API Secret'


client = Client(api_key, api_secret, tld='us')

crypto_bots = {}

class PriceUpdater:
    def __init__(self, crypto_bots):
        self.crypto_bots = crypto_bots
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.update_prices)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def get_current_price(self):
        tickers = client.get_all_tickers()
        return tickers

    def update_prices(self):
      while self.running:
        current_price = self.get_current_price()
        for instance in crypto_bots.values():
            instance.price_check(current_price)
            
        #print(current_price)
        time.sleep(1)
            

class MartBot:
    def __init__(self, key, variables):
        self.key = key
        self.total_profit = 0
        self.transactions = 0
        self.sell_price = None
        self.symbol = variables[0]
        self.profit = float(variables[2])
        
        string_scale = variables[1].split(',')
        self.scale = [float(i) for i in string_scale]
        self.volume_list = []
        
        self.volume = float(variables[4])
        self.orders = int(variables[5])
        self.use = float(variables[3])
        
        series_sum = (1-self.volume**self.orders)/(1-self.volume)
        x = (self.use + self.total_profit)/ series_sum
        for i in range(self.orders):
            self.volume_list.append(x*self.volume**i)
            
        self.price_bought = []
        self.amount_bought = []
        self.bought = 0
        
    def main(self, new_price):
        if self.bought ==0:
            self.buy_order(new_price)
            
        elif self.bought >= 1 and self.bought <= self.orders and new_price <= self.price_bought[-1]*(1-self.scale[self.bought]/100):
            self.buy_order(new_price)
            
        elif self.bought >= 1 and new_price >= self.sell_price:
            self.sell_order(new_price)
            
        else:
            pass
        
        
    def price_check(self, tickers):
        for ticker in tickers:
            symbol_check = ticker['symbol']
            if symbol_check == self.symbol:
                new_price = float(ticker['price'])
                
        self.main(new_price)
    
    def buy_order(self, new_price):
        #buy_order = client.order_market_buy(symbol = self.symbol, quantity = float(Decimal(self.volume_list[self.bought]/ new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
        
        self.price_bought.append(new_price)
        self.amount_bought.append(float(Decimal(self.volume_list[self.bought]/ new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
        print(self.price_bought)
        print(self.amount_bought)
        
        total_cost = 0
        for i in range(len(self.price_bought)):
            total_cost += self.price_bought[i] * self.amount_bought[i]
        self.sell_price = total_cost*(1+self.profit/100)/sum(self.amount_bought)    
        
        self.bought += 1
                
        print(f'{self.key} bought')
            
    def sell_order(self, new_price):
        #sell_order = client.order_market_sell(symbol = self.symbol, quantity = float(Decimal(sum(self.amount_bought)).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))    

        print(sum(self.amount_bought))
        
        total_round_cost = 0
        for i in range(len(self.price_bought)):
            total_round_cost += self.price_bought[i] * self.amount_bought[i]
        round_profit = round(new_price* sum(self.amount_bought) - total_round_cost, 4)
        self.total_profit += round_profit
        
        print(round_profit)
        print(self.total_profit)
        
        self.price_bought = []
        self.amount_bought = []
        self.sell_price = None
        self.bought = 0
        self.transactions += 1
        
        


bots_dict = {
    'martingale_bot1' : ['ETHUSDT', '0.5,0.6,0.7,0.8,0.9,1', '0.3', '100', '1.5', '6']
}

for key in bots_dict.keys():
    print(key)
    instance = MartBot(key, bots_dict[key])
    crypto_bots[key] = instance

price_updater = PriceUpdater(crypto_bots)
price_updater.start()

time.sleep(5)

price_updater.stop()