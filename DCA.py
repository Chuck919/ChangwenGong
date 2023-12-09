from API import api_key, api_secret

from binance.client import Client
import time
import threading
from decimal import Decimal, ROUND_DOWN


#api_key = 'API Key'
#api_secret = 'API Secret'


client = Client(api_key, api_secret, tld='us')

bots_dict = {'DCAbot1':['BTCUSDT', '1000', '10', '1 seconds']}

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
    while True:
      current_price = self.get_current_price()
      for instance in crypto_bots.values():
        instance.price_check(current_price)
      time.sleep(1)

class DCABot:
    def __init__(self, key, variables):
        self.key = key
        self.symbol = variables[0]
        self.amount = float(variables[1])
        self.buys = float(variables[2])
        a, b = variables[3].split(' ')
        a = float(a)
        
        if b == 'seconds':
            self.interval = a
        
        elif b == 'minutes':
            self.interval = a*60
            
        elif b == 'hours':
            self.interval = a*60*60
        
        else:
            print('invalid')
            exit()
            
        self.original_interval = self.interval
        
    def price_check(self, tickers):
        for ticker in tickers:
            symbol_check = ticker['symbol']
            if symbol_check == self.symbol:
                new_price = float(ticker['price'])
        if new_price == None:
            print('symbol was not found')
            exit()
        self.main(new_price)
        
    def main(self, new_price):
        if self.interval <= 0:
            self.buy_order(new_price)
            self.interval = self.original_interval
            
        else:
            self.interval -= 1
            
    def buy_order(self, price):
        buy_amount = (self.amount/self.buys)/price
        #buy_order = client.order_market_buy(symbol = self.symbol, quantity=float(Decimal(buy_amount).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
        self.amount -= self.amount/self.buys
        self.buys -= 1
        if self.amount <= 0 or self.buys <= 0:
            self.stop_bot()
            
        print(f'{self.key} bought {buy_amount}. {self.amount} left')
            
    def stop_bot(self):
        raise Exception(f'bot {self.key} stopped')
        

      
crypto_bots = {}

for key in bots_dict.keys():
    print(key)
    if 'DCA' in key:
        instance = DCABot(key, bots_dict[key])
    crypto_bots[key] = instance
    
price_updater = PriceUpdater(crypto_bots)
print('start')

price_updater.update_prices()    
    