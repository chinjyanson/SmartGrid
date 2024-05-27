import numpy as np
from scipy.optimize import minimize
import time
import server_data as data
import train as train

def maximize_profit_mpc(initial_storage_level, max_storage_capacity, predicted_buy_prices, predicted_sell_prices, predicted_demand, time_step=5, horizon=5):
    
    storage = initial_storage_level
    total_profit = 0
    n = len(predicted_buy_prices)

    # x is an array with first half representing buy energy and second half representing sell energy
    # This means that x[t] is amount of energy to buy at time t and x[horizon + t] is amount of energy to sell at time t
    def objective(x, storage, predicted_buy_prices, predicted_sell_prices):
        profit = 0
        storage_level = storage
        for t in range(horizon):
            buy_energy = x[t]
            sell_energy = x[horizon + t]
            storage_level += buy_energy - sell_energy
            profit -= buy_energy * predicted_buy_prices[t]
            profit += sell_energy * predicted_sell_prices[t]
        return -profit  # Minimize negative profit = maximize positive profit

    def constraint(x, storage, t):
        buy_energy = x[t]
        sell_energy = x[horizon + t]
        return storage + buy_energy - sell_energy - max_storage_capacity

    def storage_constraint(x, storage, t):
        return storage - max_storage_capacity

    def no_simultaneous_buy_sell_constraint(x, t):
        buy_energy = x[t]
        sell_energy = x[horizon + t]
        return buy_energy * sell_energy  # Ensures one is zero if the other is not

    for t in range(0, n - horizon, time_step):
        start_time = time.time()
        # Simulate real-time change in energy_in and energy_used
        energy_in = get_current_energy_in()
        energy_used = get_current_energy_used()

        
        
        # Update storage with net input energy
        net_input = energy_in - energy_used
        storage += net_input

        storage = min(max(storage, 0), max_storage_capacity)

        # Get current buy and sell prices
        current_buy_price, current_sell_price = get_current_buy_sell_prices()

        x0 = np.zeros(2 * horizon)  # Initial guess
        bounds = [(0, max_storage_capacity)] * horizon + [(0, max_storage_capacity)] * horizon  # Bounds for buy/sell
        constraints = [{'type': 'ineq', 'fun': constraint, 'args': (storage, i)} for i in range(horizon)] + \
                      [{'type': 'ineq', 'fun': storage_constraint, 'args': (storage, i)} for i in range(horizon)] + \
                      [{'type': 'eq', 'fun': no_simultaneous_buy_sell_constraint, 'args': (i,)} for i in range(horizon)]
        
        result = minimize(objective, x0, args=(storage, predicted_buy_prices[t:t + horizon], predicted_sell_prices[t:t + horizon]), 
                          bounds=bounds, constraints=constraints, method='SLSQP', options={'ftol': 1e-5})
        
        if result.success:
            optimal_buy_sell = result.x
            # Update storage and profit based on actual prices
            actual_buy_energy = optimal_buy_sell[0]
            actual_sell_energy = optimal_buy_sell[horizon]
            storage += actual_buy_energy - actual_sell_energy
            total_profit -= actual_buy_energy * current_buy_price
            total_profit += actual_sell_energy * current_sell_price

            storage = min(max(storage, 0), max_storage_capacity)

            print(f"Cycle {t//time_step + 1}:")
            print(f"  Energy Bought: {actual_buy_energy} kWh")
            print(f"  Energy Sold: {actual_sell_energy} kWh")
            print(f"  Energy Stored: {storage} kWh")
            print(f"  Energy Used: {energy_used} kWh")
            print(f"  Solar Energy: {energy_in} kWh")
            print(f"  Current Buy Price: {current_buy_price} £/kWh")
            print(f"  Current Sell Price: {current_sell_price} £/kWh")

        else: 
            print(f"Cycle {t//time_step + 1}: Optimization failed")
            print(result.message)
        
        # Factor in the code time taken into the sleep time (call every 5 seconds regardless of code)
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
trainer = train.Train()
predicted_buy_prices = trainer.query_model('buy_price')
print("tried buy price")

predicted_sell_prices = trainer.query_model('sell_price')
print("tried sell price")

predicted_demand = trainer.query_model('demand')
print("tried demand")

initial_storage_level = 0
max_storage_capacity = 50

max_profit = maximize_profit_mpc(initial_storage_level, max_storage_capacity, predicted_buy_prices, predicted_sell_prices, predicted_demand)
print(f"Maximum Profit: {max_profit}")
