import server_data_test as data
from train_test import Train
import time

'''
most naive solution to the problem
'''

# Constants
STORAGE_CAPACITY = 50  # Maximum storage capacity in Joules

def naive_smart_grid_optimizer(data_buffers, t, current_storage):
    total_profit = 0

    solar_energy = data_buffers['sun'][-1]
    actual_demand = data_buffers['demand'][-1]
    buy_price = data_buffers['buy_price'][-1]
    sell_price = data_buffers['sell_price'][-1]
    solar_energy = solar_energy / 30

    serve = data.server_data()
    serve.deferables()
    deferables = serve.parsed_data['deferables']
    print(deferables)


    # Total energy needed
    total_demand = actual_demand
    
    # Schedule deferable demand within its window
    for ele in deferables:
        if ele["start"] <= t < ele["end"]:
            total_demand += ele["energy"] / (ele["end"] - ele["start"])  # Spread energy requirement over time window

    # Use solar energy first to meet demand
    if solar_energy >= total_demand:
        solar_energy -= total_demand
        total_demand = 0
    else:
        total_demand -= solar_energy
        solar_energy = 0

    # Use stored energy if solar is insufficient
    if total_demand > 0:
        if current_storage >= total_demand:
            current_storage -= total_demand
            total_demand = 0
        else:
            total_demand -= current_storage
            current_storage = 0

    # Buy energy from the grid if necessary
    if total_demand > 0:
        # Buy enough energy to meet the remaining demand
        energy_bought = total_demand
        total_profit -= energy_bought * buy_price  # Subtract the cost of buying energy
        current_storage += energy_bought
        current_storage = min(current_storage, STORAGE_CAPACITY)  # Ensure storage does not exceed capacity

    # Handle excess solar energy
    if solar_energy > 0:
        # First try to store the excess energy
        if current_storage + solar_energy <= STORAGE_CAPACITY:
            current_storage += solar_energy
        else:
            # If storage is full, sell the excess energy
            excess_energy = current_storage + solar_energy - STORAGE_CAPACITY
            total_profit += excess_energy * sell_price  # Add the revenue from selling energy
            current_storage = STORAGE_CAPACITY

    # Print current state for debugging
    print("for cycle: " + str(t))
    print(f"Time {t}: Demand={actual_demand}, Solar={solar_energy}, Storage={current_storage}, Buy Price={buy_price}, Sell Price={sell_price}")
    print(f"Total Profit={total_profit}")

    return total_profit, current_storage

if __name__ == "__main__":
    # Run the optimizer
    print("Running naive")