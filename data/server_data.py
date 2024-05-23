import requests
import sys
sys.path.insert(0, '/home/ilan/Desktop/SmartGrid')

import utils

class server_data:
    def __init__(self):
        self.url = 'https://icelec50015.azurewebsites.net'
        self.json = ""
        self.data_points = 60

    def set_json(self, endpoint):
        print(self.url+endpoint)
        self.json = requests.get(self.url+endpoint).json()
        print(self.json)

    def get_historical_prices(self):
        out = {'buy_price':[], 'demand':[], 'sell_price':[]}

        for s in ['buy_price', 'demand', 'sell_price']:
            for i in range(self.data_points):
                out[s].append(self.json[i][s])

        return out

if (__name__ == "__main__"):
    serve = server_data()
    serve.set_json('/yesterday')

    buy = serve.get_historical_prices()['buy_price']
    sell = serve.get_historical_prices()['sell_price']

    utils.plot_datas(sell, None)