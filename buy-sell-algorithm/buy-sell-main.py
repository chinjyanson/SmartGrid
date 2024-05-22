#assume we have prices = [...]
#assume we know flexible_use = [...] and immediate_use =[unpredictable]
#assume we know the capacity = [...]

naive

if prices <= threshould:
    we sell if enough expected usage (including flywheel) and if storage is full until prices <= threshould 
    we buy if not enough generated power to cover expected usage and if storage is not full until prices > threshould
elif prices > threshould:
    we sell if enough expected usage (including flywheel) and if storage is full until prices <= threshould 
    we buy if not enough generated power to cover expected usage and if storage is not full until prices < threshould



Greedy:
import numpy as np

# Example data
time_slots = 24  # number of time slots in a day
energy_prices = np.sin(2 * np.pi * np.arange(time_slots) / time_slots) + np.random.normal(0, 0.1, time_slots)

scheduled_tasks = [
    {'id': 1, 'energy_required': 5, 'time_window': (0, 23)},  # Can be scheduled anytime within the day
    {'id': 2, 'energy_required': 3, 'time_window': (8, 18)},  # Can be scheduled between 8 AM and 6 PM
]

immediate_tasks = [
    {'id': 1, 'energy_required': 4, 'time': 10}, 
    {'id': 2, 'energy_required': 2, 'time': 14},  
]

energy_storage_capacity = 10
initial_storage = 5
max_storage = 10
storage_efficiency = 0.9

# Initialize storage level
storage_level = initial_storage

# Task schedule result (0: not scheduled, 1: scheduled)
schedule = np.zeros((len(scheduled_tasks), time_slots))

# Function to schedule immediate tasks
def schedule_immediate_tasks():
    for task in immediate_tasks:
        t = task['time']
        if storage_level >= task['energy_required']:
            storage_level -= task['energy_required']
        else:
            needed_energy = task['energy_required'] - storage_level
            storage_level = 0
            # Buy energy from grid
            total_cost = needed_energy * energy_prices[t]
            print(f"Immediate task {task['id']} at time {t} costs {total_cost:.2f}")

# Function to manage energy storage
def manage_energy_storage():
    global storage_level
    for t in range(time_slots):
        if energy_prices[t] < np.mean(energy_prices):  # Price is low, store energy
            store_amount = min(max_storage - storage_level, 1)  # Store 1 unit if possible
            storage_level += store_amount * storage_efficiency
            print(f"Stored {store_amount:.2f} units at time {t} (Storage level: {storage_level:.2f})")
        else:  # Price is high, retrieve energy
            retrieve_amount = min(storage_level, 1)  # Retrieve 1 unit if possible
            storage_level -= retrieve_amount
            print(f"Retrieved {retrieve_amount:.2f} units at time {t} (Storage level: {storage_level:.2f})")

# Function to schedule remaining tasks
def schedule_remaining_tasks():
    global storage_level
    for task in scheduled_tasks:
        scheduled = False
        for t in range(task['time_window'][0], task['time_window'][1] + 1):
            if storage_level >= task['energy_required']:
                storage_level -= task['energy_required']
                schedule[task['id'] - 1, t] = 1
                scheduled = True
                break
        if not scheduled:
            for t in range(task['time_window'][0], task['time_window'][1] + 1):
                if storage_level < task['energy_required']:
                    needed_energy = task['energy_required'] - storage_level
                    storage_level = 0
                    # Buy energy from grid
                    total_cost = needed_energy * energy_prices[t]
                    print(f"Scheduled task {task['id']} at time {t} costs {total_cost:.2f}")
                    schedule[task['id'] - 1, t] = 1
                    break

# Schedule immediate tasks
schedule_immediate_tasks()

# Manage energy storage
manage_energy_storage()

# Schedule remaining tasks
schedule_remaining_tasks()

print("Final schedule:")
print(schedule)
print(f"Final storage level: {storage_level:.2f}")


ILP:


import numpy as np
import pulp

# Example data
time_slots = 24  # number of time slots in a day
energy_prices = np.sin(2 * np.pi * np.arange(time_slots) / time_slots) + np.random.normal(0, 0.1, time_slots)

scheduled_tasks = [
    {'id': 1, 'energy_required': 5, 'time_window': (0, 23)},  # Can be scheduled anytime within the day
    {'id': 2, 'energy_required': 3, 'time_window': (8, 18)},  # Can be scheduled between 8 AM and 6 PM
    # Add more tasks as needed
]

immediate_tasks = [
    {'id': 1, 'energy_required': 4, 'time': 10},
    {'id': 2, 'energy_required': 2, 'time': 14}, 
    # Add more tasks as needed
]

energy_storage_capacity = 10
initial_storage = 5
max_storage = 10
storage_efficiency = 0.9

# Initialize the ILP problem
prob = pulp.LpProblem("Energy_Optimization", pulp.LpMaximize)

# Decision variables
use_energy = pulp.LpVariable.dicts("use_energy", ((task['id'], t) for task in scheduled_tasks for t in range(time_slots)),
                                   lowBound=0, cat='Continuous')
store_energy = pulp.LpVariable.dicts("store_energy", range(time_slots), lowBound=0, cat='Continuous')
retrieve_energy = pulp.LpVariable.dicts("retrieve_energy", range(time_slots), lowBound=0, cat='Continuous')
storage_level = pulp.LpVariable.dicts("storage_level", range(time_slots + 1), lowBound=0, upBound=max_storage, cat='Continuous')

# Initial storage level constraint
prob += storage_level[0] == initial_storage

# Objective: Maximize profit (minimize cost)
prob += pulp.lpSum(
    [-energy_prices[t] * (use_energy[task['id'], t] + retrieve_energy[t]) + energy_prices[t] * store_energy[t] for task in scheduled_tasks for t in range(time_slots)]
), "Total_Profit"

# Constraints
for t in range(time_slots):
    # Energy storage dynamics
    prob += storage_level[t + 1] == storage_level[t] + store_energy[t] * storage_efficiency - retrieve_energy[t], f"Storage_Balance_{t}"
    
    # Storage capacity constraints
    prob += store_energy[t] <= max_storage - storage_level[t], f"Max_Store_{t}"
    prob += retrieve_energy[t] <= storage_level[t], f"Max_Retrieve_{t}"
    
    # Ensure storage level is within bounds
    prob += storage_level[t] <= max_storage, f"Storage_Capacity_{t}"

# Scheduled tasks constraints
for task in scheduled_tasks:
    prob += pulp.lpSum([use_energy[task['id'], t] for t in range(task['time_window'][0], task['time_window'][1] + 1)]) == task['energy_required'], f"Task_Energy_{task['id']}"

# Immediate tasks constraints
for task in immediate_tasks:
    t = task['time']
    prob += pulp.lpSum([use_energy[task['id'], t]]) == task['energy_required'], f"Immediate_Task_{task['id']}"

# Solve the problem
prob.solve()

# Print the results
print("Status:", pulp.LpStatus[prob.status])
for task in scheduled_tasks:
    for t in range(time_slots):
        print(f"Use energy for task {task['id']} at time {t}: {pulp.value(use_energy[task['id'], t])}")

print("Total profit:", pulp.value(prob.objective))

