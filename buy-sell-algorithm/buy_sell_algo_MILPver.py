import numpy as np
import pulp
import server_data as data
import train as train
import time

def maximize_profit_mip(initial_buffer_level, max_buffer_capacity, predicted_buy_prices, predicted_sell_prices, time_step=5, horizon=10):
    buffer = initial_buffer_level
    total_profit = 0
    n = len(predicted_buy_prices)

    for t in range(0, n - horizon, time_step):
        # Simulate real-time change in energy_in and energy_used
        energy_in = get_current_energy_in()
        energy_used = get_current_energy_used()  # TODO: + scheduled_use()

        # Update buffer with net input energy
        net_input = energy_in - energy_used
        buffer += net_input
        buffer = min(max(buffer, 0), max_buffer_capacity)

        # Get current buy and sell prices
        current_buy_price, current_sell_price = get_current_buy_sell_prices()

        # Define the problem
        prob = pulp.LpProblem("Maximize_Profit", pulp.LpMaximize)

        # Decision variables
        buy_energy = [pulp.LpVariable(f'buy_energy_{i}', lowBound=0, upBound=max_buffer_capacity) for i in range(horizon)]
        sell_energy = [pulp.LpVariable(f'sell_energy_{i}', lowBound=0, upBound=max_buffer_capacity) for i in range(horizon)]
        buy_indicator = [pulp.LpVariable(f'buy_indicator_{i}', cat='Binary') for i in range(horizon)]
        sell_indicator = [pulp.LpVariable(f'sell_indicator_{i}', cat='Binary') for i in range(horizon)]

        # Objective function
        profit = pulp.lpSum([sell_energy[i] * predicted_sell_prices[t + i] - buy_energy[i] * predicted_buy_prices[t + i] for i in range(horizon)])
        prob += profit

        # Constraints
        for i in range(horizon):
            prob += buffer + buy_energy[i] - sell_energy[i] <= max_buffer_capacity
            prob += buffer + buy_energy[i] - sell_energy[i] >= 0
            prob += buy_energy[i] <= max_buffer_capacity * buy_indicator[i]
            prob += sell_energy[i] <= max_buffer_capacity * sell_indicator[i]
            prob += buy_indicator[i] + sell_indicator[i] <= 1  # Ensures mutual exclusivity

        # Solve the problem
        prob.solve()

        # Extract results
        optimal_buy_energy = [pulp.value(buy_energy[i]) for i in range(horizon)]
        optimal_sell_energy = [pulp.value(sell_energy[i]) for i in range(horizon)]

        # Update buffer and profit based on actual prices
        actual_buy_energy = optimal_buy_energy[0]
        actual_sell_energy = optimal_sell_energy[0]
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

        # Sleep to simulate real-time decision making
        time.sleep(time_step)

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
    energy_demand = serve.parsed_data['demand']
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

max_profit = maximize_profit_mip(initial_buffer_level, max_buffer_capacity, predicted_buy_prices, predicted_sell_prices)
print(f"Maximum Profit: {max_profit}")
