import numpy as np
import pulp
import server_data as data
import threading

def problem_solver():
    # To call upon data:
    serve = data.server_data()

    # Immediate task data
    serve.live_demand()
    energy_demand= serve.parsed_data['demand']

    serve.deferables()
    deferable_demand = serve.parsed_data['deferables']

    serve.live_whole_prices()
    energy_price = serve.parsed_data['price']

    # TODO: Integrate with formula properly for solar energy prediction
    serve.live_sunshine()
    area = 1
    sun_energy = serve.parsed_data['sun']
    solar_energy = sun_energy / area

    battery_capacity = 50  # Maximum energy that can be stored in the battery in Joules (J)
    battery_initial = 0  # Initial energy in the battery
    battery_efficiency = 0.9  # Efficiency factor for charging/discharging (figure out how to get this value)

    # Creating the linear optimization model
    model = pulp.LpProblem("Energy_Optimization", pulp.LpMaximize)

    # Define the single tick
    tick = energy_demand["tick"]

    # Decision variables
    grid_purchase = pulp.LpVariable("Grid_Purchase", lowBound=0)
    grid_sale = pulp.LpVariable("Grid_Sale", lowBound=0)
    battery_storage = pulp.LpVariable("Battery_Storage", lowBound=0, upBound=battery_capacity)
    battery_charge = pulp.LpVariable("Battery_Charge", lowBound=0)
    battery_discharge = pulp.LpVariable("Battery_Discharge", lowBound=0)
    energy_used = pulp.LpVariable("Energy_Used", lowBound=0)

    # Objective function: Maximize profit (revenue from selling energy - cost of purchasing energy)
    profit = grid_sale * energy_price["sell_price"] - grid_purchase * energy_price["buy_price"]
    model += profit

    # Constraints
    # Energy balance for the tick
    regular_demand = energy_demand["demand"]
    total_deferable_demand = sum(d["energy"] for d in deferable_demand if d["start"] <= tick <= d["end"])
    model += (energy_used == regular_demand + total_deferable_demand)

    # Battery storage dynamics for a single tick (assume initial storage)
    model += (battery_storage == battery_initial + battery_charge * battery_efficiency - battery_discharge * (1 / battery_efficiency))

    # Ensure energy balance
    model += (energy_used == solar_energy + grid_purchase + battery_discharge - battery_charge - grid_sale)

    # Solve the model
    model.solve()

    # Output the results
    print(f"Tick {tick}:")
    print(f"  Grid Purchase: {pulp.value(grid_purchase)}")
    print(f"  Grid Sale: {pulp.value(grid_sale)}")
    print(f"  Battery Storage: {pulp.value(battery_storage)}")
    print(f"  Battery Charge: {pulp.value(battery_charge)}")
    print(f"  Battery Discharge: {pulp.value(battery_discharge)}")
    print(f"  Energy Used: {pulp.value(energy_used)}")
    print(f"Total Profit: {pulp.value(model.objective)}")


def repeat():
    threading.Timer(5, repeat).start()
    problem_solver()

repeat()