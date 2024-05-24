import pulp

# Example data (to be replaced with actual data)
num_jobs = 5
num_time_slots = 10

# Amount of energy used by job j at time slot i
use = pulp.LpVariable.dicts("use", ((j, i) for j in range(num_jobs) for i in range(num_time_slots)), 
                            lowBound=0, cat='Integer')

# Binary variables to indicate if a job is active at a given time slot
active = pulp.LpVariable.dicts("active", ((j, i) for j in range(num_jobs) for i in range(num_time_slots)),
                               cat='Binary')

# Length of each job
Time = [3, 2, 4, 1, 2]  # Example job lengths

# Capacity at each time slot
capacity = [5, 6, 5, 6, 5, 7, 5, 6, 5, 6]  # Example capacities

# Initialize the problem
prob = pulp.LpProblem("EnergyOptimization", pulp.LpMaximize)

# Objective Function: Maximize the total energy used
prob += pulp.lpSum([use[j, i] for j in range(num_jobs) for i in range(num_time_slots)]), "TotalEnergyUsed"

# Constraints
for i in range(num_time_slots):
    # Constraint: Total energy used at time slot i should not exceed the capacity
    prob += pulp.lpSum([use[j, i] for j in range(num_jobs)]) <= capacity[i], f"Capacity_Constraint_{i}"
    
    # Constraint: No more than 3 tasks running at the same time slot
    prob += pulp.lpSum([active[j, i] for j in range(num_jobs)]) <= 3, f"Task_Limit_Constraint_{i}"

for j in range(num_jobs):
    for i in range(num_time_slots):
        # Ensure that if a job is active, it is marked as such in the active variable
        prob += use[j, i] <= capacity[i] * active[j, i], f"Active_Use_Link_{j}_{i}"

# Solve the problem
prob.solve()

# Print the results
print("Status:", pulp.LpStatus[prob.status])
for j in range(num_jobs):
    for i in range(num_time_slots):
        print(f"Use[{j}, {i}] = {pulp.value(use[j, i])}")

print("Total energy used:", pulp.value(prob.objective))


#without task limit constraint
'''
import pulp

# Example data (to be replaced with actual data)
num_jobs = 5
num_time_slots = 10

# Amount of energy used by job j at time slot i
use = pulp.LpVariable.dicts("use", ((j, i) for j in range(num_jobs) for i in range(num_time_slots)), 
                            lowBound=0, cat='Integer')

# Length of each job
Time = [3, 2, 4, 1, 2]  # Example job lengths

# Capacity at each time slot
capacity = [5, 6, 5, 6, 5, 7, 5, 6, 5, 6]  # Example capacities

# Initialize the problem
prob = pulp.LpProblem("EnergyOptimization", pulp.LpMaximize)

# Objective: Maximize the total energy used
prob += pulp.lpSum([use[j, i] for j in range(num_jobs) for i in range(num_time_slots)]), "TotalEnergyUsed"

# Constraints
for i in range(num_time_slots):
    # Constraint: Total energy used at time slot i should not exceed the capacity
    prob += pulp.lpSum([use[j, i] for j in range(num_jobs)]) <= capacity[i], f"Capacity_Constraint_{i}"

for j in range(num_jobs):
    for i in range(num_time_slots - Time[j] + 1):
        # Constraint: Energy used by job j should not exceed the length of the job times the capacity
        prob += pulp.lpSum([use[j, k] for k in range(i, i + Time[j])]) <= Time[j] * min(capacity[i:i + Time[j]]), f"Job_Length_Constraint_{j}_{i}"

# Solve the problem
prob.solve()

# Print the results
print("Status:", pulp.LpStatus[prob.status])
for j in range(num_jobs):
    for i in range(num_time_slots):
        print(f"Use[{j}, {i}] = {pulp.value(use[j, i])}")

print("Total energy used:", pulp.value(prob.objective))

'''
