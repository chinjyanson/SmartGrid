import numpy as np
import cvxpy as cp
import time
import data.server_data as data
from predictions.train import Train

def maximize_profit_mpc(initial_storage_level, max_storage_capacity, predicted_buy_prices, predicted_sell_prices, time_step=5, horizon=10):
    
    storage = initial_storage_level
    total_profit = 0
    n = len(predicted_buy_prices)
    
    for t in range(0, n - horizon, time_step):
        start_time = time.time()

        # Simulate real-time change
        energy_in = get_current_energy_in()
        energy_used = get_current_energy_used()
        current_buy_price, current_sell_price = get_current_buy_sell_prices()
        
        # Update storage with net input energy
        net_input = energy_in - energy_used
        storage += net_input

        
        storage = min(max(storage, 0), max_storage_capacity)
        
        # Define optimization variables
        energy_transactions = cp.Variable(horizon)
        storage_transactions = cp.Variable(horizon)
        demands = cp.Variable(horizon, nonneg=True)
        solar_energy = cp.Variable(horizon, nonneg=True)
        storage_level = cp.Variable(horizon + 1, nonneg=True)  # Track storage level over time
        net = cp.Variable(horizon)


        pos_energy_transactions = energy_transactions * (energy_transactions > 0)
        neg_energy_transactions = energy_transactions * (energy_transactions < 0)
        pos_storage_transactions = storage_transactions * (storage_transactions > 0)
        neg_storage_transactions = storage_transactions * (storage_transactions < 0)

        # Objective function
        profit = cp.sum(neg_energy_transactions * predicted_sell_prices[t:t + horizon] - pos_energy_transactions *predicted_buy_prices[t:t + horizon])
        
          
        # Constraints
        constraints = [
            storage_level[0] == storage,  # Initial storage level
            net == solar_energy - demands + energy_transactions + storage_transactions
        ]

        for i in range(horizon):
            constraints += [
                storage_level[i + 1] == storage_level[i] - storage_transactions[i],
                storage_level[i + 1] <= max_storage_capacity,
                storage_level[i + 1] >= 0,
                neg_energy_transactions[i] <= storage_level[i],  # Can only sell if we have enough in the storage
                pos_storage_transactions[i] <= storage_level[i],  # Can only use stored energy if we have enough in the storage
                neg_storage_transactions[i] <= storage_level[i] + pos_energy_transactions[i] - neg_energy_transactions  # Can only store if there's enough capacity in the storage
            ]
        
        # Define problem
        problem = cp.Problem(cp.Maximize(profit), constraints)
        
        # Solve problem
        problem.solve(solver=cp.CBC)  # Using CBC mixed-integer solver
        
        if problem.status == cp.OPTIMAL or problem.status == cp.FEASIBLE:
            optimal_energy_transaction = energy_transactions.value[0]
            optimal_storage_transaction = storage_transactions.value[0]
            
            # Update storage and profit based on actual prices
            storage += optimal_storage_transaction + optimal_energy_transaction
            if optimal_energy_transaction < 0:
                total_profit = total_profit - optimal_energy_transaction * current_sell_price 
            elif optimal_energy_transaction > 0:
                total_profit = total_profit - optimal_energy_transaction * current_buy_price

            storage = min(max(storage, 0), max_storage_capacity)
            
            print(f"Cycle {t//time_step + 1}:")
            print(f"  Energy Transaction: {optimal_energy_transaction} kWh")
            print(f"  Storage Transaction: {optimal_storage_transaction} kWh")
            print(f"  Energy Currently in storage: {storage} kWh")
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
initial_storage_level = 0
max_storage_capacity = 50

max_profit = maximize_profit_mpc(initial_storage_level, max_storage_capacity, predicted_buy_prices, predicted_sell_prices)
print(f"Maximum Profit: {max_profit}")
