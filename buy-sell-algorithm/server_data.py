import requests
import sys
sys.path.insert(0, '/Users/ASUS/SmartGrid')

import utils

class server_data:
    def __init__(self):
        self.url = 'https://icelec50015.azurewebsites.net'
        self.json = ""
        self.data_points = 60
        self.parsed_data = {'buy_price':[], 'demand':[], 'sell_price':[], 'sun':[], 'deferables':[]}
        self.deffs = []

    def set_json(self, endpoint):
        print(self.url+endpoint)
        self.json = requests.get(self.url+endpoint).json()

    def set_historical_prices(self):
        self.set_json('/yesterday')

        for s in ['buy_price', 'demand', 'sell_price']:
            for i in range(self.data_points):
                self.parsed_data[s].append(self.json[i][s])
    
    def live_sunshine(self):
        self.set_json('/sun')
        self.parsed_data['sun'] = self.json['sun']

    def live_prices(self):
        self.set_json('/price')
        self.parsed_data['buy_price'] = self.json['buy_price']
        self.parsed_data['sell_price'] = self.json['sell_price']

    def live_whole_prices(self):
        self.set_json('/price')
        self.parsed_data['price'] = self.json

    def live_demand(self):
        self.set_json('/demand')
        self.parsed_data['demand'] = self.json['demand']

    def deferables(self):
        self.set_json('/deferables')
        self.parsed_data['deferables'] = self.json  

if (__name__ == "__main__"):
    serve = server_data()
    serve.set_historical_prices()

    buy = serve.parsed_data['buy_price']
    sell = serve.parsed_data['sell_price']

    serve.live_sunshine()
    print(serve.parsed_data['sun'])