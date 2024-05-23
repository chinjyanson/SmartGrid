import numpy as np
import pulp
import threading
import server_data as data

battery_capacity = 50  # Maximum capacity of the battery
battery_efficiency = 0.9  # Efficiency of charging/discharging the battery
battery_initial = 0  # Initial amount of energy in the battery

# Lookahead table of energy prices (array of 30 values for buy and 30 for sell prices)
lookahead_prices = [
    [0.2, 0.15], [0.18, 0.14], [0.21, 0.16], [0.19, 0.15], [0.22, 0.18], [0.17, 0.14],
    [0.16, 0.13], [0.2, 0.17], [0.21, 0.16], [0.18, 0.15], [0.22, 0.18], [0.19, 0.14],
    [0.17, 0.13], [0.16, 0.12], [0.15, 0.11], [0.18, 0.14], [0.19, 0.15], [0.2, 0.16],
    [0.21, 0.17], [0.22, 0.18], [0.23, 0.19], [0.24, 0.2], [0.22, 0.18], [0.21, 0.17],
    [0.2, 0.16], [0.19, 0.15], [0.18, 0.14], [0.17, 0.13], [0.16, 0.12], [0.15, 0.11]
]

n_ticks = len(lookahead_prices)  # Number of time ticks based on lookahead prices length

# Initialize the battery storage
battery_storage = battery_initial

def data_call():
    serve = data.server_data()

    # Immediate task data
    serve.live_demand()
    energy_demand= serve.parsed_data['demand']

    serve.deferables()
    defer_demands = serve.parsed_data['deferables']

    serve.live_whole_prices()
    energy_price = serve.parsed_data['price']

    # TODO: Integrate with formula properly for solar energy prediction
    serve.live_sunshine()
    area = 1
    sun_energy = serve.parsed_data['sun']
    solar_energy = sun_energy / area

    return energy_demand, defer_demands, energy_price, solar_energy

def problem_solver(tick=0, battery_storage=battery_initial):
    energy_demand, defer_demands, energy_price, solar_energy = data_call()

    # Initialize the problem
    prob = pulp.LpProblem("EnergyOptimization", pulp.LpMaximize)

    # Define decision variables
    buy = [pulp.LpVariable(f"buy_{t}", lowBound=0) for t in range(n_ticks)]
    sell = [pulp.LpVariable(f"sell_{t}", lowBound=0) for t in range(n_ticks)]
    store = [pulp.LpVariable(f"store_{t}", lowBound=0, upBound=battery_capacity) for t in range(n_ticks)]
    use = [pulp.LpVariable(f"use_{t}", lowBound=0) for t in range(n_ticks)]

    # Objective function: maximize profit (minimize cost) over the entire horizon
    prob += pulp.lpSum([lookahead_prices[t][1] * sell[t] - lookahead_prices[t][0] * buy[t] for t in range(n_ticks)])

    # Constraints

    # Initial battery storage
    prob += store[0] == battery_storage

    for t in range(n_ticks):
        energy_demand_t = energy_demand["demand"] if t == 0 else 0
        solar_energy_t = solar_energy

        # Energy balance constraint for each tick
        if t == 0:
            prob += buy[t] + solar_energy_t + battery_storage * battery_efficiency - store[t] - sell[t] - use[t] == energy_demand_t
        else:
            prob += buy[t] + solar_energy_t + store[t-1] * battery_efficiency - store[t] - sell[t] - use[t] == 0

    # Deferrable demand constraints
    for defer_demand in defer_demands:
        total_energy = defer_demand["energy"]
        duration = defer_demand["end"] - defer_demand["start"] + 1
        energy_per_tick = total_energy / duration
        for t in range(defer_demand["start"], defer_demand["end"] + 1):
            if t < n_ticks:
                prob += use[t] >= energy_per_tick

    # Battery capacity constraints
    for t in range(n_ticks):
        prob += store[t] <= battery_capacity  # Battery capacity should not be exceeded
        prob += store[t] >= 0  # Battery storage should not be negative

    # Solve the problem
    prob.solve()

    # Results
    if pulp.LpStatus[prob.status] == 'Optimal':
        for t in range(n_ticks):
            print(f"Tick {tick + t}: Buy {buy[t].varValue:.2f}, Sell {sell[t].varValue:.2f}, Store {store[t].varValue:.2f}, Use {use[t].varValue:.2f}")
        # Update battery storage for the next tick
        battery_storage = store[0].varValue
    else:
        print("Optimization failed:", pulp.LpStatus[prob.status])

    # Schedule the next tick
    if tick + 1 < n_ticks:
        threading.Timer(5, problem_solver, args=(tick + 1, battery_storage)).start()

# Start the problem solver
problem_solver()