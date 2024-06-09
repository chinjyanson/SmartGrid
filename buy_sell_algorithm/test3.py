import numpy as np
import cvxpy as cp
import data.server_data as data
import predictions.train as train

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

def maximize_profit_mpc(initial_storage_level, data_buffers, predictions_buffer, t, horizon):

    MAX_POWER = 20
    MAX_STORAGE_CAPACITY = 50
    predicted_buy_prices = predictions_buffer['buy_price']
    predicted_sell_prices = predictions_buffer['sell_price']
    predicted_demand = predictions_buffer['demand']

    storage = initial_storage_level
    total_profit = 0

    # Simulate real-time change
    energy_in = data_buffers['sun'][-1] * 0.1
    energy_used = data_buffers['demand'][-1]
    current_buy_price = data_buffers['buy_price'][-1]
    current_sell_price = data_buffers['sell_price'][-1]
    energy_in = energy_in * 0.1

    # Update predictions
    predicted_buy_prices[t] = current_buy_price
    predicted_sell_prices[t] = current_sell_price

    serve = data.server_data()
    serve.deferables()
    deferables = serve.parsed_data['deferables']

    # Define optimization variables
    energy_transactions = cp.Variable(horizon)
    storage_transactions = cp.Variable(horizon)
    solar_energy = cp.Variable(horizon, nonneg=True)
    demand = cp.Variable(horizon, nonneg=True)
    deferable_demand = cp.Variable((len(deferables), horizon), nonneg=True)
    storage_level = cp.Variable(horizon + 1, nonneg=True)  # Track storage level over time
=======
    storage_level = cp.Variable(horizon + 1, nonneg=True)
>>>>>>> d6c7984 ([ayc122] <fix> almost working with deferables)

    # Positive and negative parts of energy transactions
    pos_energy_transactions = cp.Variable(horizon, nonneg=True)
    neg_energy_transactions = cp.Variable(horizon, nonneg=True)
    pos_storage_transactions = cp.Variable(horizon, nonneg=True)
    neg_storage_transactions = cp.Variable(horizon, nonneg=True)

    # Deferable demand variables
    deferable_demand = [cp.Variable(horizon, nonneg=True) for _ in deferables]

    # Objective function
    profit = cp.sum(cp.multiply(neg_energy_transactions, predicted_sell_prices[t:t + horizon]) - cp.multiply(pos_energy_transactions, predicted_buy_prices[t:t + horizon]))

    # Constraints for deferable demands
    constraints = []
    for idx, ele in enumerate(deferables):
        constraints += [
            cp.sum(deferable_demand[idx, ele["start"]:ele["end"]]) == ele["energy"],  # Ensure total energy demand is met within the allowed window
        ]

    # Other constraints
    constraints += [
        storage_level[0] == storage,  # Initial storage level
        solar_energy[0] == energy_in,  # Initial solar energy input
        demand[0] == energy_used,  # Initial demand is the current energy used
    # Constraints
    constraints = [
        storage_level[0] == storage,
        solar_energy[0] == energy_in,
        demand[0] == energy_used,  # Set initial demand to energy used
        energy_transactions == pos_energy_transactions - neg_energy_transactions,
        storage_transactions == pos_storage_transactions - neg_storage_transactions,
        pos_energy_transactions + solar_energy - demand - neg_energy_transactions >= 0,
        energy_transactions + storage_transactions + solar_energy - demand >= 0,
        solar_energy[0] - demand[0] <= -energy_transactions[0] - storage_transactions[0],
    ]

    for i in range(horizon):
        total_demand = demand[i] + cp.sum(deferable_demand[:, i])
        constraints += [
            total_demand <= MAX_DEMAND_CAPACITY,
            storage_level[i + 1] == storage_level[i] - storage_transactions[i],
=======
>>>>>>> d6c7984 ([ayc122] <fix> almost working with deferables)
            storage_level[i + 1] <= MAX_STORAGE_CAPACITY,
            storage_level[i + 1] >= 0,
            neg_energy_transactions[i] <= storage_level[i],
            pos_energy_transactions[i] <= MAX_STORAGE_CAPACITY - storage_level[i],
        ]

    for i in range(1, horizon):  # Starting from 1 since solar_energy[0] is fixed to energy_in
        constraints += [
            solar_energy[i] == 0,  # Worst-case scenario
            demand[i] == predicted_demand[t + i],  # Set subsequent demands to predicted demand
        ]

    for idx, ele in enumerate(deferables):
        start, end, energy = ele['start'], ele['end'], ele['energy']
        constraints += [
            cp.sum(deferable_demand[idx][start:end]) == energy,  # Ensure total deferable demand is met
        ]
        for i in range(horizon):
            if i < start or i >= end:
                constraints += [
                    deferable_demand[idx][i] == 0  # Set deferable demand to zero outside the specified time window
                ]
            else:
                constraints += [
                    deferable_demand[idx][i] <= (MAX_POWER - demand[i]),  # Ensure total demand + deferable demand does not exceed max power
                    deferable_demand[idx][i] >= 0  # Ensure non-negativity
                ]


    # Define problem
    problem = cp.Problem(cp.Maximize(profit), constraints)

    # Solve problem
    problem.solve(solver=cp.CBC)

    if problem.status == cp.INFEASIBLE:
        print("INFEASIBLE SOLUTION")
        # Use naive solution if solution is infeasible
        if energy_in >= energy_used:
            energy_in -= energy_used
            energy_used = 0
        else:
            energy_used -= energy_in
            energy_in = 0

        if energy_used > 0:
            if storage >= energy_used:
                storage -= energy_used
                energy_used = 0
            else:
                energy_used -= storage
                storage = 0

        if energy_in > 0:
            if storage + energy_in <= MAX_STORAGE_CAPACITY:
                storage += energy_in
            else:
                excess_energy = storage + energy_in - MAX_STORAGE_CAPACITY
                total_profit += excess_energy * current_sell_price
                storage = MAX_STORAGE_CAPACITY

        print(f" Energy In: {energy_in} kWh")
        print(f" Energy Used: {energy_used} kWh")
        print(f" Energy Currently in storage: {storage} kWh")
        print(f" Predicted Demand: {predicted_demand[t:t + horizon]}")
        print(f" Predicted Buy Prices: {predicted_buy_prices[t:t + horizon]}")
        print(f" Predicted Sell Prices: {predicted_sell_prices[t:t + horizon]}")

    elif problem.status == cp.OPTIMAL or problem.status == cp.FEASIBLE:
        optimal_energy_transaction = energy_transactions.value[0]
        optimal_storage_transaction = storage_transactions.value[0]
        for idx in range(len(deferable_list)):
            deferable_list[idx].energyDone += deferable_demand[idx][0].value

        # Update storage and profit based on actual prices
        if optimal_energy_transaction < 0:
            total_profit -= optimal_energy_transaction * current_sell_price
        elif optimal_energy_transaction > 0:
            total_profit -= optimal_energy_transaction * current_buy_price

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
        print(f" Predicted Demand: {predicted_demand[t:t + horizon]}")
        print(f" Predicted Buy Prices: {predicted_buy_prices[t:t + horizon]}")
        print(f" Predicted Sell Prices: {predicted_sell_prices[t:t + horizon]}")
        for idx in range(len(deferable_list)):
            print(f"  Deferable Demand {idx}: {deferable_demand[idx].value}")
        for idx in range(len(deferable_list)):
            print(f"  Deferables: {deferable_list[idx].start}, {deferable_list[idx].end}, {deferable_list[idx].energyTotal}, {deferable_list[idx].energyDone}")

    else:
        print(f"Optimization failed")
        print(problem.status)

    return total_profit, storage