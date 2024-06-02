import requests
import sys
import time

class server_data:
    def __init__(self) -> None:
        self.url = 'https://icelec50015.azurewebsites.net'
        self.json = ""
        self.data_points = 60
        self.parsed_data = {'buy_price':[], 'demand':[], 'sell_price':[], 'sun':[], 'deferables':[]}
        self.tick = 0

    def set_json(self, endpoint) -> None:
        print(self.url+endpoint)
        try:
            self.json = requests.get(self.url+endpoint).json()
        except:
            print("Cannot get data from external server")
            sys.exit(1)

    def set_historical_prices(self):
        self.set_json('/yesterday')
        for s in ['buy_price', 'demand', 'sell_price']:
            self.parsed_data[s] = []
            for i in range(self.data_points):
                self.parsed_data[s].append(self.json[i][s])
    
    def live_sunshine(self):
        self.set_json('/sun')
        self.parsed_data['sun'] = self.json['sun']
        self.tick = self.json['tick']

    def live_prices(self):
        self.set_json('/price')
        self.parsed_data['buy_price'] = self.json['buy_price']
        self.parsed_data['sell_price'] = self.json['sell_price']
        self.tick = self.json['tick']

    def live_demand(self):
        self.set_json('/demand')
        self.parsed_data['demand'] = self.json['demand']
        self.tick = self.json['tick']

    # deferables is not working (parsing wrong data)
    def deferables(self):
        self.set_json('/deferables')
        for s in ['start', 'end', 'energy']:
            self.parsed_data[s] = []
            for i in range(3):
                self.parsed_data[s].append(self.json[i][s])
        #self.parsed_data['deferables'] = self.json

    def get_ticks(self):
        self.set_json('/sun')
        self.parsed_data['tick'] = self.json['tick']

if (__name__ == "__main__"):
    while True:
        serve = server_data()
        serve.deferables()
        print(serve.parsed_data['start'])
        print(serve.parsed_data['end'])
        print(serve.parsed_data['energy'])
        serve.get_ticks()
        print(serve.parsed_data['tick'])
        time.sleep(5)

    