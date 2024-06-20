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
    if deferables is None:
        return 0
    for idx, ele in enumerate(deferables):
        deferablesList.append(Deferables(ele['start'], ele['end'], ele['energy'], 0, idx))
    return deferablesList

deferable_list = []


class AlgoVar:
    def __init__(self, tick, optimal_energy_transactions, optimal_storage_transactions, solar_energy, demand, tick_profit, current_buy_price, current_sell_price, storage, base_demand):
        self.tick = tick
        self.optimal_energy_transactions = optimal_energy_transactions
        self.optimal_storage_transactions = optimal_storage_transactions
        self.solar_energy = solar_energy
        self.demand = demand
        self.base_demand = base_demand
        self.buy_price = current_buy_price
        self.sell_price = current_sell_price
        self.profit = tick_profit
        self.storage = storage

def maximize_profit_mpc(initial_storage_level, data_buffers, predictions_buffer, t, horizon, deferables):
    global deferable_list
    if deferables:
        deferable_list = parseDeferables(deferables)

    if t == 0:
        for idx in range(len(deferable_list)):
            deferable_list[idx].energyDone = 0

    MAX_STORAGE_CAPACITY = 50
    MAX_DEMAND_CAPACITY = 20
    POWER_LOSS = 2
    predicted_buy_prices = [ele/100 for ele in predictions_buffer['buy_price']]
    predicted_sell_prices = [ele/100 for ele in predictions_buffer['sell_price']]
    predicted_dem = predictions_buffer['demand']
    predicted_sun = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                     0, 0, 0, 0, 0, 0, 10, 20, 30, 40, 
                     49, 58, 66, 74, 80, 86, 91, 95, 97, 99, 
                     100, 99, 97, 95, 91, 86, 80, 74, 66, 58, 
                     49, 40, 30, 20, 10, 0, 0, 0, 0, 0, 
                     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    predicted_demand = []
    
    for ele in predicted_dem:
        predicted_demand.append(ele)
        if ele > MAX_DEMAND_CAPACITY:
            ele = MAX_DEMAND_CAPACITY
        predicted_demand.append(ele+POWER_LOSS)

    # for idx in range(len(deferable_list)):
    #     if deferable_list[idx].start <= t < deferable_list[idx].end:
    #         deferable_demand += deferable_list[idx].energyTotal / (deferable_list[idx].end - deferable_list[idx].start) 

    print(f"initial_storage_level {initial_storage_level}")

    storage = initial_storage_level
    tick_profit = 0

    # Simulate real-time change
    energy_in = data_buffers['sun'][-1]
    energy_used = data_buffers['demand'][-1]
    current_buy_price = data_buffers['buy_price'][-1]/100
    current_sell_price = data_buffers['sell_price'][-1]/100
    energy_in = energy_in * 0.05
    energy_used += POWER_LOSS
    base_demand = energy_used

    #print(f"opt demand {energy_used} kWh")
    #energy_used = min(energy_used, MAX_DEMAND_CAPACITY)

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

    deferable_demand = [cp.Variable(horizon, nonneg=True) for _ in deferable_list]
    # Binary variables to enforce mutual exclusivity
    x = cp.Variable(horizon, boolean=True)  # Binary variable

    # Objective function
    profit = cp.sum(cp.multiply(neg_energy_transactions, predicted_buy_prices[t:t+horizon]) - cp.multiply(pos_energy_transactions, predicted_sell_prices[t:t+horizon]))

    # Constraints
    M = 1e5  # Large constant for big-M method
    constraints = [
        storage_level[0] == storage,  # Initial storage level
        solar_energy[0] == energy_in,
        demand[0] == energy_used,
        energy_transactions == pos_energy_transactions - neg_energy_transactions,
        storage_transactions == pos_storage_transactions - neg_storage_transactions,
        energy_transactions + storage_transactions + solar_energy - demand - sum(deferable_demand[idx] for idx in range(len(deferable_list))) >= 0,
        pos_energy_transactions <= M * (1 - x),
        pos_storage_transactions <= M * x
    ]

    for i in range(horizon):
        constraints += [
            # demand[i] <= MAX_DEMAND_CAPACITY,
            storage_level[i + 1] == storage_level[i] - storage_transactions[i],
            storage_level[i + 1] <= MAX_STORAGE_CAPACITY,
            storage_level[i + 1] >= 0,
            neg_energy_transactions[i] <= storage_level[i],  # Can only sell if we have enough in the storage
            pos_energy_transactions[i] <= MAX_STORAGE_CAPACITY - storage_level[i],  # Can only buy if we have enough storage capacity
            solar_energy[i] >= 0,
            demand[i] >= 0,
            deferable_demand[0][i] + deferable_demand[1][i] + deferable_demand[2][i] + demand[i] <= MAX_DEMAND_CAPACITY,
            #sum(deferable_demand[idx][i] for idx in range(len(deferable_list))) + demand[i] <= MAX_DEMAND_CAPACITY,
        ]

    for i in range(1, horizon):  # Starting from 1 since solar_energy[0] is fixed to energy_in
        constraints += [
            solar_energy[i] == predicted_sun[t + i] * 0.05,
            demand[i] == predicted_demand[i] ,  # Predicted demand
        ]

    for idx, deferable in enumerate(deferable_list):
        start = max(deferable.start - t, 0)
        end = min(deferable.end - t, horizon)
        energy_needed = deferable.energyTotal - deferable.energyDone

        constraints += [
            cp.sum(deferable_demand[idx][start:end]) >= energy_needed,
            cp.sum(deferable_demand[idx][:start]) == 0,
            cp.sum(deferable_demand[idx][end:]) == 0,
        ]

        # for i in range(horizon):
        #     # min_energy_fulfilled = energy_needed / (end - start) * 0.1  # Ensure minimum energy allocation
        #     constraints += [
        #         # deferable_demand[idx][i] >= min_energy_fulfilled,
        #         deferable_demand[0][i] + deferable_demand[1][i] + deferable_demand[2][i] + demand[i] <= MAX_DEMAND_CAPACITY,
        #     ]

    # Define problem
    problem = cp.Problem(cp.Maximize(profit), constraints)

    # Solve problem
    problem.solve(solver=cp.CBC)  # Using CBC mixed-integer solver

    if problem.status == cp.INFEASIBLE:
        print("INFEASIBLE")
        naive_deferable_demand = 0
        for idx in range(len(deferable_list)):
            if deferable_list[idx].start <= t < deferable_list[idx].end:
                deferable_list[idx].energyDone += deferable_list[idx].energyTotal / (deferable_list[idx].end - deferable_list[idx].start)
                naive_deferable_demand += deferable_list[idx].energyTotal / (deferable_list[idx].end - deferable_list[idx].start)

        energy_used += naive_deferable_demand
        excess_energy = 0
        energy_bought = 0
        optimal_storage_transaction = 0

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
                optimal_storage_transaction += energy_used
                energy_used = 0
            else:
                energy_used -= storage
                storage = 0

        if energy_used > 0:
            energy_bought = energy_used
            tick_profit -= energy_bought * current_sell_price  # Subtract the cost of buying energy
            energy_used = 0

        if energy_in > 0:
            if storage + energy_in <= MAX_STORAGE_CAPACITY:
                optimal_storage_transaction -= energy_in
                storage += energy_in
            else:
                excess_energy = storage + energy_in - MAX_STORAGE_CAPACITY
                tick_profit += excess_energy * current_buy_price  # Add the revenue from selling energy
                storage = MAX_STORAGE_CAPACITY
            energy_in = 0

        optimal_energy_transaction = energy_bought - excess_energy


    elif problem.status == cp.OPTIMAL or problem.status == cp.FEASIBLE:
        optimal_energy_transaction = energy_transactions.value[0]
        optimal_storage_transaction = storage_transactions.value[0]
        for idx in range(len(deferable_list)):
            deferable_list[idx].energyDone += deferable_demand[idx][0].value

        # Update storage and profit based on actual prices
        if optimal_energy_transaction < 0:
            tick_profit -= optimal_energy_transaction * current_buy_price
        elif optimal_energy_transaction > 0:
            tick_profit -= optimal_energy_transaction * current_sell_price

        # Ensure storage is within bounds after transactions
        storage -= optimal_storage_transaction
        storage = min(max(storage, 0), MAX_STORAGE_CAPACITY)

        print(f"  Energy Transaction: {optimal_energy_transaction} kWh")
        print(f"  Storage Transaction: {optimal_storage_transaction} kWh")
        print(f"  Energy Currently in storage: {storage} kWh")
        print(f"  Energy Used: {energy_used} kWh")
        print(f"  Solar Energy: {energy_in} kWh")
        print(f" storage: {storage}" )
        # print(f"  Current Buy Price: {current_buy_price} £/kWh")
        # print(f"  Current Sell Price: {current_sell_price} £/kWh")
        # print(f" energy_transactions.value: {energy_transactions.value}")
        # print(f" storage_transactions.value: {storage_transactions.value}")
        # print(f" solar_energy: {solar_energy.value}")
        # print(f"Demand Value: {demand.value[0] + sum(deferable_demand[idx][0].value for idx in range(len(deferable_list)))}")
        # print(f" demand: {demand.value}")
        # print(f" storage: {storage_level.value}")
        # print(f" Predicted Buy Prices: {predicted_buy_prices[t:t + horizon]}")
        # print(f" Predicted Sell Prices: {predicted_sell_prices[t:t + horizon]}")
        # for idx in range(len(deferable_list)):
        #     print(f"  Deferable Demand {idx}: {deferable_demand[idx].value}")
        # for idx in range(len(deferable_list)):
        #     print(f"  Deferables: {deferable_list[idx].start}, {deferable_list[idx].end}, {deferable_list[idx].energyTotal}, {deferable_list[idx].energyDone}")
        energy_used = demand.value[0] + sum(deferable_demand[idx][0].value for idx in range(len(deferable_list)))
    else:
        print(f"   Optimization failed")
        print(problem.status)

    algovar = AlgoVar(t, optimal_energy_transaction, optimal_storage_transaction, energy_in, energy_used, tick_profit, current_buy_price, current_sell_price, storage, base_demand)

    return algovar

if __name__ == "__main__":
    print("Running opt solution")