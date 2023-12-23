from API import api_key, api_secret

from binance.client import Client
import time
import threading
from decimal import Decimal, ROUND_DOWN
import numpy as np


#api_key = 'API Key'
#api_secret = 'API Secret'


client = Client(api_key, api_secret, tld='us')


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
      time.sleep(60)
        
class Algorithms:
    def __init__ (self):
        pass
    
    def ema(self, data, window):
        alpha = 2/(window +1)
        ema = [data[0]]
        
        for i in range(1, len(data)):
            ema_value = alpha * data[i] + (1 - alpha) * ema[-1]
            ema.append(ema_value)
            
        return ema
    
    def macd(self, closing_prices, short_window, long_window, signal_window):
        short_ema = self.ema(closing_prices, short_window)
        
        long_ema = self.ema(closing_prices, long_window)
        
        macd_line = [short - long for short, long in zip(short_ema, long_ema)]
        
        signal_line = self.ema(macd_line, signal_window)
        
        macd_histogram = [
            macd - signal for macd, signal in zip(macd_line, signal_line)
        ]
        
        return [macd_line, signal_line, macd_histogram]
    
    def rsi(self, closing_prices, window):
        price_changes = np.diff(closing_prices)

        # Calculate gains and losses
        gains = np.where(price_changes > 0, price_changes, 0)
        losses = np.where(price_changes < 0, -price_changes, 0)

        # Calculate average gains and average losses for the specified window
        avg_gains = np.mean(gains[:-window])
        avg_losses = np.mean(losses[:-window])

        # Calculate initial RS (Relative Strength)
        if avg_losses == 0:
            rs = np.inf  # Set RS to positive infinity to avoid division by zero
        else:
            rs = avg_gains / avg_losses

        # Calculate RSI
        rsi = 100 - (100 / (1 + rs))

        return rsi
    
    def roc(self, closing_prices, n):
        roc_values = []
        
        for i in range(n, len(closing_prices)):
            current_price = closing_prices[i]
            price_n_periods_ago = closing_prices[i-n]
            
            roc = ((current_price - price_n_periods_ago) / price_n_periods_ago) * 100
            roc_values.append(roc)
            
        return roc_values
    
    def heikin_ashi(self, klines):
        ha_data = []
        
        ha_open = float(klines[0][1])
        for kline in klines:
            timestamp, open_price, high, low, close, volume, *_ = kline
            open_price, high, low, close, volume = map(float, [open_price, high, low, close, volume])
            
            ha_close = (open_price + high + low + close)/4
            ha_data.append([timestamp, ha_open, max(high, ha_close), min(low, ha_close), ha_close, volume])
            
            ha_open = (ha_open + ha_close) / 2
            
        return ha_data
            

    
class Check:
    def __init__(self):
        pass
    
    def roc_check(self, roc):
        if roc[-2] < 0 and roc[-1] > 0:
            return 'BUY'
        
        elif roc[-2] >0 and roc[-1] <0:
            return 'SELL'
        
        else:
            return None
    
    def macd_check(self, macd):
        if macd[2][-2] < 0 and macd[2][-1] > 0:
            return 'BUY'
        
        elif macd[2][-2] > 0 and macd[2][-1] < 0:
            return 'SELL'
        
        else:
            return None
        
    def rsi_check(self, rsi):
        return 'SELL' if rsi >= 70 else 'BUY' if rsi <= 30 else None
    
    
class AlgoBot:
    def __init__(self, key, variables):
        self.key = key
        self.symbol = variables['symbol']
        self.checks = {
            key: value
            for index, (key, value) in enumerate(variables.items()) if index >= 3
        }
        
        self.signals = {key : None for key in self.checks.keys()}
        self.use = variables['use']
        self.heikin = variables['Heikin Ashi']
        self.bought = None
        self.amount = None
        self.transactions = 0
        self.profit = 0
        
    def main(self, new_price):
        interval = Client.KLINE_INTERVAL_1MINUTE
        limit = 1000
        
        klines = client.get_historical_klines(self.symbol, interval, limit=limit)
        
        if self.heikin == 'y' or self.heikin == 'Y':
            klines = algos.heikin_ashi(klines)
        
        closing_prices = [float(kline[4]) for kline in klines]
        
        if 'macd' in self.checks:
            params = self.checks.get('macd')
            print(f'macd: {algos.macd(closing_prices, params[0], params[1], params[2])}')
            signal = check.macd_check(
                algos.macd(closing_prices, params[0], params[1], params[2]))
            
            self.signals['macd'] = signal
            
        if 'rsi' in self.checks:
            params = self.checks.get('rsi')
            print(f'rsi: {algos.rsi(closing_prices, params)}')
            
            signal = check.rsi_check(algos.rsi(closing_prices, params))
            self.signals['rsi'] = signal
            
        if 'roc' in self.checks:
            params = self.checks.get('roc')
            print(f'roc : {algos.roc(closing_prices, params)}')
            
            signal = check.roc_check(algos.roc(closing_prices, params))
            self.signals['roc'] = signal
            
        print(self.signals)
        
        unique_values = set(self.signals.values())
        if len(unique_values) == 1 and 'BUY' in unique_values and self.bought == None:
            self.buy_order(new_price)
            
        elif len(unique_values) == 1 and 'SELL' in unique_values and self.bought != None:
            self.sell_order(new_price)
            
        else:
            pass
        
    def buy_order(self, new_price):
        #buy_order = client.order_market_buy(symbol = self.symbol, quantity=float(Decimal(self.use/new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN)))
        
        self.amount = float(Decimal(self.use/new_price).quantize(Decimal('0.0001'), rounding=ROUND_DOWN))
        self.bought = new_price
        
        print(f'{self.key} bought {self.amount} at {self.bought}')
        
    def sell_order(self, new_price):
        #sell_order = client.order_market_sell(symbol = self.symbol, quantity = self.amount)
        self.transactions += 1
        
        round_profit = ((new_price - self.bought)*self.amount/self.bought) #*(1-selling fee)
        
        self.profit += round_profit
        self.use += round_profit
        self.bought = None
        
        print(f'{self.key} sold for {round_profit}')
        
    
    def price_check(self, tickers):
        for ticker in tickers:
            symbol_check = ticker['symbol']
            if symbol_check == self.symbol:
                new_price = float(ticker['price'])
        self.main(new_price)       




algos = Algorithms()
check = Check()


bots_dict = {
    'Algobot1': {
        'symbol' : 'BTCUSDT',
        'use' : 100,
        'Heikin Ashi' : 'y',
        'roc': 9,
        'macd' :[12, 26, 9],
        'rsi' : 9
    }
}

crypto_bots = {}

for key in bots_dict.keys():
    print(key)
    instance = AlgoBot(key, bots_dict[key])
    crypto_bots[key] = instance
    
price_updater = PriceUpdater(crypto_bots)
print('start')

price_updater.update_prices()

time.sleep(61)

price_updater.stop()