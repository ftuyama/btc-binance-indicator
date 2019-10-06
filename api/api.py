#!/usr/bin/env python3

import requests

class Api():
    """API methods

        These methods manipulate API
    """
    def blockchain_btc_price(self):
        try:
            r = requests.get('https://blockchain.info/ticker')
            return r.json()['USD']['last']
        except Exception as e:
            print(e)
            return None

    def binance_futures_history(self):
        try:
            r = requests.get('https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=1m')
            data = r.json()
            return [int(float(d[4])) for d in data]
        except Exception as e:
            print(e)
            return None

    def binance_futures_price(self):
        try:
            r = requests.get('https://fapi.binance.com/fapi/v1/ticker/price?symbol=BTCUSDT')
            return float(r.json()['price'])
        except Exception as e:
            print(e)
            return None

    def huobi_symbol_price(self, symbol):
        try:
            r = requests.get('https://api.huobi.pro/market/detail/merged?symbol=' + symbol)

            if symbol == 'btcusdt':
                return round(r.json()['tick']['close'])
            else:
                return r.json()['tick']['close']
        except Exception as e:
            print(e)
            return None

    def binance_symbol_avg_price(self, symbol):
        try:
            r = requests.get('https://api.binance.com/api/v1/klines?symbol=' + symbol.upper() + 'USDT&interval=1m&limit=1')
            return int(r.json()[0][4].split('.')[0])
        except Exception as e:
            print(e)
            return None
