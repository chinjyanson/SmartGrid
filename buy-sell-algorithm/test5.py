import numpy as np
from scipy.optimize import minimize
import time
import matplotlib as plt
import server_data as data

def maximize_profit_mpc(initial_buffer_level, max_buffer_capacity, predicted_buy_prices, predicted_sell_prices, time_step=5, horizon=10):
    buffer = initial_buffer_level
    total_profit = 0
    n = len(predicted_buy_prices)

    # x is an array with first half representing buy energy and second half representing sell energy
    # This means that x[t] is amount of energy to buy at time t and x[horizon + t] is amount of energy to sell at time t
    def objective(x, buffer, predicted_buy_prices, predicted_sell_prices):
        profit = 0
        buffer_level = buffer
        for t in range(horizon):
            buy_energy = x[t]
            sell_energy = x[horizon + t]
            buffer_level += buy_energy - sell_energy
            profit -= buy_energy * predicted_buy_prices[t]
            profit += sell_energy * predicted_sell_prices[t]
        return -profit  # Minimize negative profit = maximize positive profit

    def constraint(x, buffer, t):
        buy_energy = x[t]
        sell_energy = x[horizon + t]
        return buffer + buy_energy - sell_energy - max_buffer_capacity

    def buffer_constraint(x, buffer, t):
        buy_energy = x[t]
        sell_energy = x[horizon + t]
        return buffer + buy_energy - sell_energy

    for t in range(0, n - horizon, time_step):
        # Simulate real-time change in energy_in and energy_used
        energy_in = get_current_energy_in()
        energy_used = get_current_energy_used()
        
        # Update buffer with net input energy
        net_input = energy_in - energy_used
        buffer += net_input

        # Get current buy and sell prices
        current_buy_price, current_sell_price = get_current_buy_sell_prices()

        x0 = np.zeros(2 * horizon)  # Initial guess
        bounds = [(0, max_buffer_capacity)] * horizon + [(0, max_buffer_capacity)] * horizon  # Bounds for buy/sell
        constraints = [{'type': 'ineq', 'fun': constraint, 'args': (buffer, i)} for i in range(horizon)] + \
                      [{'type': 'ineq', 'fun': buffer_constraint, 'args': (buffer, i)} for i in range(horizon)]
        
        result = minimize(objective, x0, args=(buffer, predicted_buy_prices[t:t + horizon], predicted_sell_prices[t:t + horizon]), 
                          bounds=bounds, constraints=constraints)
        
        if result.success:
            optimal_buy_sell = result.x
            # Update buffer and profit based on actual prices
            actual_buy_energy = optimal_buy_sell[0]
            actual_sell_energy = optimal_buy_sell[horizon]
            buffer += actual_buy_energy - actual_sell_energy
            total_profit -= actual_buy_energy * current_buy_price
            total_profit += actual_sell_energy * current_sell_price

            print(f"Cycle {t//time_step + 1}:")
            print(f"  Energy Bought: {actual_buy_energy} kWh")
            print(f"  Energy Sold: {actual_sell_energy} kWh")
            print(f"  Energy Stored: {buffer} kWh")
            print(f"  Energy Used: {energy_used} kWh")

        time.sleep(time_step)
    
    return total_profit

# Example usage with mock functions for current energy
def get_current_energy_in():
    serve = data.server_data()
    # Immediate task data
    serve.live_sunshine()
    area = 1000
    sun_energy = serve.parsed_data['sun']
    solar_energy = sun_energy / area
    return solar_energy

def get_current_energy_used():
    serve = data.server_data()
    # Immediate task data
    serve.live_demand()
    energy_demand= serve.parsed_data['demand']
    return energy_demand

def get_current_buy_sell_prices():
    serve = data.server_data()
    serve.live_prices()
    current_buy_price = serve.parsed_data['buy_price']
    current_sell_price = serve.parsed_data['sell_price']
    return current_buy_price, current_sell_price
# Example data
predicted_buy_prices = [
    10.7422509253765045, 10.2408420501390114, 10.7417511266066489, 1.06936452410405569,
    10.015446540839825218, 10.646511979863557, 10.05495912021415106, 10.5192874889764744,
    10.972610428342263, 10.49862227191646236, 10.8622085737855102, 10.7330479544661466,
    10.49420828762588587, 10.37392589065818405, 10.8387867224732112, 10.08811229149438449,
    10.9380218215202984, 10.08594784795195143, 10.274278510107858, 10.3741991023712671,
    10.20197924333773432, 10.3013195791528199, 10.9945303020699188, 10.7260816547509658,
    10.9977209720767929, 10.35960845726367074, 10.738752464505671, 10.936677422040921,
    10.28755465331238483, 10.3734234545984727, 1.8215499104690176, 10.11955601173369768,
    10.2532473072991761, 10.6319831588347471, 10.1503563487731917, 10.8709569032195323,
    10.7216381940885112, 10.5942189574294577, 1.8363208485697761, 10.41386121814881827,
    10.49059314367218754, 1.720680530367957, 10.34111326631053285, 10.3406577488224808,
    10.2743140840667153, 10.6878782017951669, 10.6183503355264123, 10.6467363787054432,
    10.7294034149868627, 10.014102001704026312, 10.09303679885047089, 10.15991409014207192,
    10.4299530571512661, 10.06798160263867958, 10.535982895811561, 10.3114280224147168,
    10.9966936406284793, 10.9160705198779759, 10.3995848673058702, 10.07073433158143017
]
  # Predicted buy prices for future time steps
predicted_sell_prices = [
    0.48346614194152926, 0.24585679317713371, 0.17236870397626192, 0.49690805066356225,
    0.35425188417565623, 0.6420416900356466, 0.5500960448354515, 0.7325338233837977,
    0.8210762787940382, 0.9778315914739988, 0.5176982875713605, 0.17741163158740303,
    0.39195608405281623, 0.7480825845224283, 0.18552256356548558, 0.595300949026113,
    0.2790779951002814, 0.10649022859547064, 0.4708158866885215, 0.5973734566937144,
    0.17919747756326365, 0.36604055363994636, 0.14106094086515353, 0.8535808545174639,
    0.6842072536636111, 0.6120690061138778, 0.8908386784292595, 0.6872851213829316,
    0.12401099618906286, 0.9752203083877007, 0.5246773115335305, 0.35738795092397346,
    0.3271121430626571, 0.9260478170443892, 0.6123204101482925, 0.6608960228817324,
    0.7003725832222099, 0.7468041633110031, 0.042329613845338065, 0.8107269271336462,
    0.7564533459563278, 0.5841567744612964, 0.17098582713362886, 0.4084709117860976,
    0.20123693004399756, 0.08141764834927778, 0.7560782620512114, 0.7932105735093583,
    0.9324709114517025, 0.03921676658908668, 0.11744371636682427, 0.0968345859482278,
    0.2222988880995721, 0.746412326286461, 0.8658688452214195, 0.9965943696210909,
    0.3367602548635118, 0.6799710030377742, 0.776980380830512, 0.8351526909823707
]
  # Predicted sell prices for future time steps
initial_buffer_level = 10
max_buffer_capacity = 20

max_profit = maximize_profit_mpc(initial_buffer_level, max_buffer_capacity, predicted_buy_prices, predicted_sell_prices)
print(f"Maximum Profit: {max_profit}")

