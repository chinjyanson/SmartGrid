import numpy as np
import cvxpy as cp

class Deferables:
    def __init__(self, start, end, energyTotal, energyDone, idx) -> None:
        self.start = start
        self.end = end
        self.energyTotal = energyTotal
        self.energyDone = energyDone
        self.idx = idx

def parseDeferables(deferables):
    deferablesList = []
    for idx, ele in enumerate(deferables):
        deferablesList.append(Deferables(ele['start'], ele['end'], ele['energy'], 0, idx))
    return deferablesList

deferable_list = []

def maximize_profit_mpc(initial_storage_level, data_buffers, predictions_buffer, t, horizon, deferables):
    deferable_demand = 0
    global deferable_list
    if deferables:
        deferable_list = parseDeferables(deferables)

    MAX_STORAGE_CAPACITY = 50
    MAX_DEMAND_CAPACITY = 20
    predicted_buy = predictions_buffer['buy_price']
    predicted_sell = predictions_buffer['sell_price']
    predicted_dem = predictions_buffer['demand']
    predicted_sun = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 20, 30, 40, 49, 58, 66, 74, 80, 86, 91, 95, 97, 99, 100, 99, 97, 95, 91, 86, 80, 74, 66, 58, 49, 40, 30, 20, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    predicted_buy_prices = []
    predicted_sell_prices = []
    predicted_demand = []

    for idx in range(len(deferable_list)):
        if deferable_list[idx].start <= t < deferable_list[idx].end:
            deferable_demand += deferable_list[idx].energyTotal / (deferable_list[idx].end - deferable_list[idx].start) 

    print(f"Deferable Demand: {deferable_demand} kWh")

    for ele in predicted_buy:
        predicted_buy_prices.append(ele/100)
    for ele in predicted_sell:
        predicted_sell_prices.append(ele/100)
    for ele in predicted_dem:
        predicted_demand.append(ele+10)

    storage = initial_storage_level
    total_profit = 0

    # Simulate real-time change
    energy_in = data_buffers['sun'][-1]
    energy_used = data_buffers['demand'][-1] + deferable_demand + 10
    current_buy_price = data_buffers['buy_price'][-1]/100
    current_sell_price = data_buffers['sell_price'][-1]/100
    energy_in = energy_in * 0.05

    print(f"opt demand {energy_used} kWh")
    # Update predictions
    predicted_buy_prices[t] = current_buy_price
    predicted_sell_prices[t] = current_sell_price

    # Define optimization variables
    energy_transactions = cp.Variable(horizon)
    storage_transactions = cp.Variable(horizon)
    solar_energy = cp.Variable(horizon, nonneg=True)
    demand = cp.Variable(horizon, nonneg=True)
    storage_level = cp.Variable(horizon + 1, nonneg=True)  # Track storage level over time

    # Positive and negative parts of energy transactions
    pos_energy_transactions = cp.Variable(horizon, nonneg=True)
    neg_energy_transactions = cp.Variable(horizon, nonneg=True)
    pos_storage_transactions = cp.Variable(horizon, nonneg=True)
    neg_storage_transactions = cp.Variable(horizon, nonneg=True)

    # Binary variables to enforce mutual exclusivity
    x = cp.Variable(horizon, boolean=True)  # Binary variable

    # Objective function
    profit = cp.sum(cp.multiply(neg_energy_transactions, predicted_buy[t:t+horizon]) - cp.multiply(pos_energy_transactions, predicted_sell[t:t+horizon]))

    # Constraints
    M = 1e5  # Large constant for big-M method
    constraints = [
        storage_level[0] == storage,  # Initial storage level
        solar_energy[0] == energy_in,
        demand[0] == energy_used,
        energy_transactions == pos_energy_transactions - neg_energy_transactions,
        storage_transactions == pos_storage_transactions - neg_storage_transactions,
        energy_transactions + storage_transactions + solar_energy - demand >= 0,
        pos_energy_transactions <= M * (1 - x),
        pos_storage_transactions <= M * x
    ]

    for i in range(horizon):
        constraints += [
            storage_level[i + 1] == storage_level[i] - storage_transactions[i],
            storage_level[i + 1] <= MAX_STORAGE_CAPACITY,
            storage_level[i + 1] >= 0,
            neg_energy_transactions[i] <= storage_level[i],  # Can only sell if we have enough in the storage
            pos_energy_transactions[i] <= MAX_STORAGE_CAPACITY - storage_level[i],  # Can only buy if we have enough storage capacity
            solar_energy[i] >= 0,
            demand[i] >= 0
        ]

    for i in range(1, horizon):  # Starting from 1 since solar_energy[0] is fixed to energy_in
        constraints += [
            solar_energy[i] == predicted_sun[t + i] * 0.05,
            demand[i] == predicted_demand[i] + 10 + deferable_demand,  # Predicted demand
        ]

    # Define problem
    problem = cp.Problem(cp.Maximize(profit), constraints)

    # Solve problem
    problem.solve(solver=cp.CBC, verbose=True)  # Using CBC mixed-integer solver

    if problem.status == cp.INFEASIBLE:
        print("Infeasible")

        total_demand = energy_used
        solar_energy = energy_in
        excess_energy = 0
        # Use naive solution if solution is infeasible
        if solar_energy >= total_demand:
            solar_energy -= total_demand
            total_demand = 0
        else:
            total_demand -= solar_energy
            solar_energy = 0

        # Use stored energy if solar is insufficient
        if total_demand > 0:
            if storage >= total_demand:
                storage -= total_demand
                total_demand = 0
            else:
                total_demand -= storage
                storage = 0

        # Buy energy from the grid if necessary
        if total_demand > 0:
            # Buy enough energy to meet the remaining demand
            energy_bought = total_demand
            total_profit -= energy_bought * current_sell_price  # Subtract the cost of buying energy
            total_demand = 0

        # Handle excess solar energy
        if solar_energy > 0:
            # First try to store the excess energy
            if storage + solar_energy <= MAX_STORAGE_CAPACITY:
                storage += solar_energy
            else:
                excess_energy = storage + solar_energy - MAX_STORAGE_CAPACITY
                total_profit += excess_energy * current_buy_price  # Add the revenue from selling energy
                storage = MAX_STORAGE_CAPACITY
            solar_energy = 0

        optimal_energy_transaction = energy_bought - excess_energy

    elif problem.status == cp.OPTIMAL or problem.status == cp.FEASIBLE:
        optimal_energy_transaction = energy_transactions.value[0]
        optimal_storage_transaction = storage_transactions.value[0]

        # Update storage and profit based on actual prices
        if optimal_energy_transaction < 0:
            total_profit -= optimal_energy_transaction * current_buy_price
        elif optimal_energy_transaction > 0:
            total_profit -= optimal_energy_transaction * current_sell_price

        # Ensure storage is within bounds after transactions
        storage -= optimal_storage_transaction
        storage = min(max(storage, 0), MAX_STORAGE_CAPACITY)

        print(f"  Energy Transaction: {optimal_energy_transaction} kWh")
        print(f"  Storage Transaction: {optimal_storage_transaction} kWh")
        print(f"  Energy Currently in storage: {storage} kWh")
        print(f"  Energy Used: {energy_used} kWh")
        print(f"  Solar Energy: {energy_in} kWh")
        print(f"  Current Buy Price: {current_buy_price} £/kWh")
        print(f"  Current Sell Price: {current_sell_price} £/kWh")
        print(f" energy_transactions.value: {energy_transactions.value}")
        print(f" storage_transactions.value: {storage_transactions.value}")
        print(f" solar_energy: {solar_energy.value}")
        print(f" demand: {demand.value}")
        print(f" storage: {storage_level.value}")
        print(f" Predicted Buy Prices: {predicted_buy_prices[t:t + horizon]}")
        print(f" Predicted Sell Prices: {predicted_sell_prices[t:t + horizon]}")

    else:
        print(f"   Optimization failed")
        print(problem.status)

    return total_profit, storage, energy_used, energy_in, optimal_energy_transaction
