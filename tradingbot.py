from binance.client import Client

api_key = 'YOUR API KEY'
api_secret = 'YOUR API SECRET'

client = Client(api_key, api_secret, tld='us')

account_info = client.get_account()
print(account_info)



#buy_order = client.order_market_buy(symbol="BTCUSDT", quantity=0.001)
#sell_order = client.order_market_sell(symbol="BTCUSDT", quantity=0.001)

response = client.create_test_order(
    symbol = 'BTCUSDT',
    side = 'BUY',
    type = 'LIMIT',
    quantity = 0.001,
    price = 25000,
    timeInForce = 'GTC'
    )



def check_and_execute_trade():
    symbol = 'BTCUSDT'  # You can choose any trading pair you prefer
    buy_price = 30000.0  # Set your buy threshold
    sell_price = 40000.0  # Set your sell threshold
    
    ticker = client.get_symbol_ticker(symbol=symbol)
current_price = float(ticker['price'])
print(current_price)
    
    if current_price < buy_price:
        print(f"Buying BTC”)
        buy_order = client.order_market_buy(symbol=symbol , quantity= )

    elif current_price > sell_price:
        print(f"Selling BTC”)
        sell_order = client.order_market_sell(symbol = symbol, quantity = )

while True:
    check_and_execute_trade()
time.sleep(60)  
