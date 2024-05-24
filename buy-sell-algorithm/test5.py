import numpy as np
from scipy.optimize import minimize
import time
import matplotlib as plt
import server_data as data
import train as train

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
        start_time = time.time()
        # Simulate real-time change in energy_in and energy_used
        energy_in = get_current_energy_in()
        energy_used = get_current_energy_used()
        
        # Update buffer with net input energy
        net_input = energy_in - energy_used
        buffer += net_input

        buffer = min(max(buffer, 0), max_buffer_capacity)

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

            buffer = min(max(buffer, 0), max_buffer_capacity)

            print(f"Cycle {t//time_step + 1}:")
            print(f"  Energy Bought: {actual_buy_energy} kWh")
            print(f"  Energy Sold: {actual_sell_energy} kWh")
            print(f"  Energy Stored: {buffer} kWh")
            print(f"  Energy Used: {energy_used} kWh")
            print(f"  Solar Energy: {energy_in} kWh")
            print(f"  Current Buy Price: {current_buy_price} £/kWh")
            print(f"  Current Sell Price: {current_sell_price} £/kWh")
        
        #factor in the code time taken into the sleep time (call every 5 seconds regardless of code)
        #TODO: Figure out if the code execution time is consistently above > 5 seconds, because it could mess up future data
        end_time = time.time()
        execution_time = end_time - start_time
        print(execution_time)
        sleep_time = max(0, time_step - execution_time)
        time.sleep(sleep_time)
    
    return total_profit

# Example usage with mock functions for current energy
def get_current_energy_in():
    serve = data.server_data()
    # Immediate task data
    serve.live_sunshine()
    area = 10
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
predicted_buy_prices = train.query_model('buy_price')
print("tried buy price")

  # Predicted buy prices for future time steps
predicted_sell_prices = train.query_model('sell_price')
print("tried sell price")

  # Predicted sell prices for future time steps
initial_buffer_level = 0
max_buffer_capacity = 50

max_profit = maximize_profit_mpc(initial_buffer_level, max_buffer_capacity, predicted_buy_prices, predicted_sell_prices)
print(f"Maximum Profit: {max_profit}")

