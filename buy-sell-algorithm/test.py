import numpy as np
import cvxpy as cp
import time
import data.server_data as data
from predictions.train import Train

def maximize_profit_mpc(initial_buffer_level, max_buffer_capacity, predicted_buy_prices, predicted_sell_prices, time_step=5, horizon=10):
    
    buffer = initial_buffer_level
    total_profit = 0
    n = len(predicted_buy_prices)
    
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
        
        # Define optimization variables
        print("horizon: " + str(horizon))
        buy_sell_energy = cp.Variable(horizon)
        solar_energy = cp.Parameter(horizon, nonneg=True)
        buy_energy = cp.Variable(horizon, nonneg=True)
        sell_energy = cp.Variable(horizon, nonneg=True)
        store_energy = cp.Variable(horizon, nonneg=True)
        use_stored_energy = cp.Variable(horizon, nonneg=True)
        buffer_level = cp.Variable(horizon + 1, nonneg=True)  # Track buffer level over time
        z_buy_sell = cp.Variable(horizon, boolean=True)  # Binary variable to enforce either buy or sell
        z_store_use = cp.Variable(horizon, boolean=True)  # Binary variable to enforce either store or use stored energy
        
        # Objective function
        profit = cp.sum(cp.multiply(sell_energy, predicted_sell_prices[t:t + horizon]) - cp.multiply(buy_energy, predicted_buy_prices[t:t + horizon]))
        
        # Constraints
        constraints = [
            buffer_level[0] == buffer,  # Initial buffer level
            buy_energy + sell_energy <= max_buffer_capacity,
            store_energy + use_stored_energy <= max_buffer_capacity,
            buy_energy <= z_buy_sell * max_buffer_capacity,
            sell_energy <= (1 - z_buy_sell) * max_buffer_capacity,
            store_energy <= z_store_use * max_buffer_capacity,
            use_stored_energy <= (1 - z_store_use) * max_buffer_capacity
        ]

        for i in range(horizon):
            constraints += [
                store_energy[i] == max(0, solar_energy - energy_used - buy_energy[i]),  # Store excess solar energy
                buffer_level[i + 1] == buffer_level[i] + store_energy[i] - use_stored_energy[i],
                buffer_level[i + 1] <= max_buffer_capacity,
                buffer_level[i + 1] >= 0,
                sell_energy[i] <= buffer_level[i],  # Can only sell if we have enough in the buffer
                use_stored_energy[i] <= buffer_level[i],  # Can only use stored energy if we have enough in the buffer
                store_energy[i] <= buffer_level[i] + buy_energy[i] - sell_energy[i]  # Can only store if there's enough capacity in the buffer
            ]
        
        # Define problem
        problem = cp.Problem(cp.Maximize(profit), constraints)
        
        # Solve problem
        problem.solve(solver=cp.CBC)  # Using CBC mixed-integer solver
        
        if problem.status == cp.OPTIMAL or problem.status == cp.FEASIBLE:
            optimal_buy_energy = buy_energy.value[0]
            optimal_sell_energy = sell_energy.value[0]
            optimal_store_energy = store_energy.value[0]
            optimal_use_stored_energy = use_stored_energy.value[0]
            
            # Update buffer and profit based on actual prices
            buffer += optimal_store_energy - optimal_use_stored_energy + optimal_buy_energy - optimal_sell_energy
            
            if buy_sell_energy > 0:
                profit += buy_sell_energy * current_buy_price
            if buy_sell_energy < 0:
                profit -= buy_sell_energy * current_sell_price
            


            total_profit -= optimal_buy_energy * current_buy_price
            total_profit += optimal_sell_energy * current_sell_price
            buffer = min(max(buffer, 0), max_buffer_capacity)
            
            print(f"Cycle {t//time_step + 1}:")
            print(f"  Energy Bought: {optimal_buy_energy} kWh")
            print(f"  Energy Sold: {optimal_sell_energy} kWh")
            print(f"  Energy Stored: {optimal_store_energy} kWh")
            print(f"  Energy Used from Storage: {optimal_use_stored_energy} kWh")
            print(f"  Energy Stored in Buffer: {buffer} kWh")
            print(f"  Energy Used: {energy_used} kWh")
            print(f"  Solar Energy: {energy_in} kWh")
            print(f"  Current Buy Price: {current_buy_price} £/kWh")
            print(f"  Current Sell Price: {current_sell_price} £/kWh")
        else:
            print(f"Cycle {t//time_step + 1}: Optimization failed")
            print(problem.status)
        
        # Factor in the code time taken into the sleep time (call every 5 seconds regardless of code)
        end_time = time.time()
        execution_time = end_time - start_time
        sleep_time = max(0, time_step - execution_time)
        time.sleep(sleep_time)
    
    return total_profit

# Example usage with mock functions for current energy
def get_current_energy_in():
    serve = data.server_data()
    serve.live_sunshine()
    area = 10
    sun_energy = serve.parsed_data['sun']
    solar_energy = sun_energy / area
    return solar_energy

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

max_profit = maximize_profit_mpc(initial_buffer_level, max_buffer_capacity, predicted_buy_prices, predicted_sell_prices)
print(f"Maximum Profit: {max_profit}")
