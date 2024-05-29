import data.server_data as data
from predictions.train import Train
import time

'''
most naive solution to the problem
'''

#Logic: 
#

def get_current_energy_in():
    serve = data.server_data()
    serve.live_sunshine()
    area = 10
    sun_energy = serve.parsed_data['sun']
    solar_energy = sun_energy / area
    return solar_energy

def get_deferred_energy():
    serve = data.server_data()
    serve.deferables()
    deferred_start = serve.parsed_data['start']
    deferred_end = serve.parsed_data['end']
    deferred_energy = serve.parsed_data['energy']
    return deferred_start, deferred_end, deferred_energy

def get_current_energy_used():
    serve = data.server_data()
    serve.live_demand()
    energy_demand= serve.parsed_data['demand']
    return energy_demand

def get_current_buy_sell_prices():
    serve = data.server_data()
    serve.live_prices()
    current_buy_price = serve.parsed_data['buy_price']
    current_sell_price = serve.parsed_data['sell_price']
    return current_buy_price, current_sell_price

train = Train()
predicted_buy_prices = train.query_model('buy_price')
predicted_sell_prices = train.query_model('sell_price')
initial_buffer_level = 0
max_buffer_capacity = 50


def naive_solution(predicted__buy_prices, predicted_sell_prices, initial_buffer_level, max_buffer_capacity, time_step=5):
    average_buy_price = sum(predicted_buy_prices) / len(predicted_buy_prices)
    average_sell_price = sum(predicted_sell_prices) / len(predicted_sell_prices)

    cur_buy_price, cur_sell_price = get_current_buy_sell_prices()
    demand = get_current_energy_used()

    if cur_buy_price > average_buy_price and demand > 5:
        #use flywheel
        res = "010"
    elif cur_buy_price < average_buy_price and demand < 5:
        # buy to store in flywheel
        res = "101"
    else:
        # use PV cell
        res = "000"


    if cur_sell_price > average_sell_price:
        # sell to grid
        res += "1"
