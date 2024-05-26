import pulp
import server_data as data

def schedule_deferable_demand():
    # Fetching data from server
    serve = data.server_data()
    serve.deferables()
    deferables = serve.parsed_data['deferables']

    num_jobs = 5
    num_time_slots = 10

    # Amount of energy used by job j at time slot i
    use = pulp.LpVariable.dicts("use", ((j, i) for j in range(num_jobs) for i in range(num_time_slots)), 
                                lowBound=0, cat='Integer')

    # Binary variables to indicate if a job is active at a given time slot
    active = pulp.LpVariable.dicts("active", ((j, i) for j in range(num_jobs) for i in range(num_time_slots)),
                                   cat='Binary')

    # Time windows for each job (start time, end time)
    time_windows = [(0, 5), (3, 7), (2, 8), (0, 4), (5, 9)]  # Example time windows for each job

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
        start_time, end_time = time_windows[j]
        for i in range(num_time_slots):
            # Ensure that if a job is active, it is marked as such in the active variable
            prob += use[j, i] <= capacity[i] * active[j, i], f"Active_Use_Link_{j}_{i}"
            
            # Constraint: A job can only be active within its time window
            if i < start_time or i > end_time:
                prob += active[j, i] == 0, f"Time_Window_Constraint_{j}_{i}"

    # Solve the problem
    prob.solve()

    # Print the results
    print("Status:", pulp.LpStatus[prob.status])
    for j in range(num_jobs):
        for i in range(num_time_slots):
            print(f"Use[{j}, {i}] = {pulp.value(use[j, i])}")

    print("Total energy used:", pulp.value(prob.objective))

# Run the function
schedule_deferable_demand()
