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

def maximize_profit_mpc(initial_storage_level, data_buffers, predictions_buffer, t, horizon, deferables):
    global deferable_list
    if deferables:
        deferable_list = parseDeferables(deferables)

    if t == 0:
        for idx in range(len(deferable_list)):
            deferable_list[idx].energyDone = 0

    MAX_POWER = 30
    POWER_LOSS = 2
    LINEAR_SOLAR_DEPENDANCE = 5/100
    MAX_STORAGE_CAPACITY = 50
    predicted_buy = predictions_buffer['buy_price']
    predicted_sell = predictions_buffer['sell_price']
    predicted_demand = predictions_buffer['demand']
    predicted_buy_prices = []
    predicted_sell_prices = []

    # Convert prices to £/kWh
    for ele in predicted_buy:
        predicted_buy_prices.append(ele/100)
    for ele in predicted_sell:
        predicted_sell_prices.append(ele/100)

    storage = initial_storage_level
    total_profit = 0

    # Simulate real-time change
    energy_in = data_buffers['sun'][-1] * LINEAR_SOLAR_DEPENDANCE
    try:
        energy_used = data_buffers['demand'][-1] + POWER_LOSS
    except:
        print(data_buffers['demand'], POWER_LOSS)

    current_buy_price = data_buffers['buy_price'][-1] /100
    current_sell_price = data_buffers['sell_price'][-1] /100

    # Update predictions
    predicted_buy_prices[t] = current_buy_price 
    predicted_sell_prices[t] = current_sell_price 
    predicted_sun = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 20, 30, 40, 49, 58, 66, 74, 80, 86, 91, 95, 97, 99, 100, 99, 97, 95, 91, 86, 80, 74, 66, 58, 49, 40, 30, 20, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # Define optimization variables
    energy_transactions = cp.Variable(horizon)
    storage_transactions = cp.Variable(horizon)
    solar_energy = cp.Variable(horizon, nonneg=True)
    demand = cp.Variable(horizon, nonneg=True)
    storage_level = cp.Variable(horizon + 1, nonneg=True)

    # Positive and negative parts of energy transactions
    pos_energy_transactions = cp.Variable(horizon, nonneg=True)
    neg_energy_transactions = cp.Variable(horizon, nonneg=True)
    pos_storage_transactions = cp.Variable(horizon, nonneg=True)
    neg_storage_transactions = cp.Variable(horizon, nonneg=True)

    # Deferable demand variables and slack variables
    deferable_demand = [cp.Variable(horizon, nonneg=True) for _ in deferable_list]
    penalty_deferable = [cp.Variable(horizon, nonneg=True) for _ in deferable_list]

    # Objective function
    profit = cp.sum(cp.multiply(neg_energy_transactions, predicted_buy_prices[t:t + horizon]) - cp.multiply(pos_energy_transactions, predicted_sell_prices[t:t + horizon]))
    penalty_factor = 1.0  # Adjust based on importance of meeting deferable demands
    penalty_term = cp.sum([cp.sum(penalty_deferable[idx]) for idx in range(len(deferable_list))])
    profit -= penalty_term * penalty_factor

    # Constraints
    constraints = [
        storage_level[0] == storage,
        solar_energy[0] == energy_in,
        demand[0] == energy_used,
        energy_transactions == pos_energy_transactions - neg_energy_transactions,
        storage_transactions == pos_storage_transactions - neg_storage_transactions,
        energy_transactions + storage_transactions + solar_energy - demand - sum(deferable_demand[idx][0] for idx in range(len(deferable_list))) >= 0,
        solar_energy[0] - demand[0] - sum(deferable_demand[idx][0] for idx in range(len(deferable_list))) <= -energy_transactions[0] - storage_transactions[0], 
        pos_energy_transactions + solar_energy - demand - sum(deferable_demand[idx][0] for idx in range(len(deferable_list))) - neg_energy_transactions >= 0,
    ]

    for i in range(horizon):
        constraints += [
            storage_level[i + 1] == storage_level[i] - storage_transactions[i],
            storage_level[i + 1] <= MAX_STORAGE_CAPACITY,
            storage_level[i + 1] >= 0,
            neg_energy_transactions[i] <= storage_level[i],
            pos_energy_transactions[i] <= MAX_STORAGE_CAPACITY - storage_level[i],
            solar_energy[i] >= 0,
        ]

    for i in range(1, horizon):
        constraints += [
            solar_energy[i] == predicted_sun[t + i]/10,
            demand[i] == predicted_demand[t + i],
        ]

    for idx, deferable in enumerate(deferable_list):
        start = max(deferable.start - t, 0)
        end = min(deferable.end - t, horizon)
        energy_needed = deferable.energyTotal - deferable.energyDone

        constraints += [
            cp.sum(deferable_demand[idx][start:end]) == energy_needed
        ]

        for i in range(start, end):
            time_remaining = end - i
            penalty_multiplier = 1 / time_remaining  # Increase penalty as deadline approaches
            min_energy_fulfilled = energy_needed / (end - start) * 1  # Ensure minimum energy allocation
            constraints += [
                deferable_demand[idx][i] >= min_energy_fulfilled,
                deferable_demand[idx][i] <= MAX_POWER - demand[i],
                penalty_deferable[idx][i] >= energy_needed / (end - start) - deferable_demand[idx][i],  # Penalty for not meeting demand
                penalty_deferable[idx][i] >= 0  # Penalty must be non-negative
            ]
            profit -= penalty_multiplier * penalty_deferable[idx][i] * penalty_factor  # Time-dependent penalty

    # Define problem
    problem = cp.Problem(cp.Maximize(profit), constraints)

    # Solve problem
    problem.solve(solver=cp.CBC)

    if problem.status == cp.INFEASIBLE:
        print("INFEASIBLE SOLUTION")
        excess_energy = 0
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

        if energy_used > 0:
            energy_bought = energy_used
            total_profit -= energy_bought * current_sell_price

        if energy_in > 0:
            if storage + energy_in <= MAX_STORAGE_CAPACITY:
                storage += energy_in
            else:
                excess_energy = storage + energy_in - MAX_STORAGE_CAPACITY
                total_profit += excess_energy * current_buy_price
                storage = MAX_STORAGE_CAPACITY

        print(f" Energy In: {energy_in} kWh")
        print(f" Energy Used: {energy_used} kWh")
        print(f" Energy Currently in storage: {storage} kWh")
        print(f" Predicted Demand: {predicted_demand[t:t + horizon]}")
        print(f" Predicted Buy Prices: {predicted_buy_prices[t:t + horizon]}")
        print(f" Predicted Sell Prices: {predicted_sell_prices[t:t + horizon]}")
        for idx in range(len(deferable_list)):
            print(f"  Deferables: {deferable_list[idx].start}, {deferable_list[idx].end}, {deferable_list[idx].energyTotal}, {deferable_list[idx].energyDone}")

        optimal_energy_transaction = energy_bought - excess_energy
        for idx in range(len(deferable_list)):
            energy_used += (deferable_list[idx].energyTotal - deferable_list[idx].energyDone) / (deferable_list[idx].end - deferable_list[idx].start)

    elif problem.status == cp.OPTIMAL or problem.status == cp.FEASIBLE:
        optimal_energy_transaction = energy_transactions.value[0]
        optimal_storage_transaction = storage_transactions.value[0]

        for idx in range(len(deferable_list)):
            deferable_list[idx].energyDone += deferable_demand[idx][0].value

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
        for idx in range(len(deferable_list)):
            print(f"  Deferable Demand {idx}: {deferable_demand[idx][0].value}")
        # print(f" energy_transactions.value: {energy_transactions.value}")
        # print(f" storage_transactions.value: {storage_transactions.value}")
        # print(f" solar_energy: {solar_energy.value}")
        # print(f" demand: {demand.value}")
        print(f" storage: {storage_level.value}")
        # print(f" Predicted Demand: {predicted_demand[t:t + horizon]}")
        # print(f" Predicted Buy Prices: {predicted_buy_prices[t:t + horizon]}")
        # print(f" Predicted Sell Prices: {predicted_sell_prices[t:t + horizon]}")
        # for idx in range(len(deferable_list)):
        #     print(f"  Deferable Demand {idx}: {deferable_demand[idx].value}")
        # for idx in range(len(deferable_list)):
        #     print(f"  Deferables: {deferable_list[idx].start}, {deferable_list[idx].end}, {deferable_list[idx].energyTotal}, {deferable_list[idx].energyDone}")

        energy_used += sum(deferable_demand[idx][0].value for idx in range(len(deferable_list)))

        print(f"total profit: {total_profit}")
    else:
        print(f"Optimization failed")
        print(problem.status)

    return total_profit, storage, energy_used, energy_in, optimal_energy_transaction
