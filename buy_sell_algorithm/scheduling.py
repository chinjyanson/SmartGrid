import pulp
import data.server_data as data

def schedule_deferable_demand(t, deferables):

    num_jobs = 0
    time_windows = []
    num_time_slots = 60
    power = []
    for ele in deferables:
        num_jobs += 1
        time_windows.append((ele["start"], ele["end"]))
        power.append(ele["energy"] / (ele["end"] - ele["start"]))

    # Amount of energy used by job j at time slot i
    use = pulp.LpVariable.dicts("use", ((j, i) for j in range(num_jobs) for i in range(num_time_slots)), 
                                lowBound=0, cat='Integer')

   # Initialize the problem
    prob = pulp.LpProblem("EnergyOptimization", pulp.LpMaximize)

    # Objective: Maximize the total energy used
    prob += pulp.lpSum([use[j, i] for j in range(num_jobs) for i in range(num_time_slots)]), "TotalEnergyUsed"

    # Constraints
    for i in range(num_time_slots):
        # Constraint: Total energy used at time slot i should not exceed the capacity
        prob += pulp.lpSum([use[j, i] for j in range(num_jobs)]) <= capacity[i], f"Capacity_Constraint_{i}"

    for j in range(num_jobs):
        for i in range(num_time_slots - time_windows[j] + 1):
            # Constraint: Energy used by job j should not exceed the length of the job times the capacity
            prob += pulp.lpSum([use[j, k] for k in range(i, i + time_windows[j])]) <= time_windows[j] * min(capacity[i:i + time_windows[j]]), f"Job_Length_Constraint_{j}_{i}"

    # Solve the problem
    prob.solve()

    # Print the results
    print("Status:", pulp.LpStatus[prob.status])
    for j in range(num_jobs):
        for i in range(num_time_slots):
            print(f"Use[{j}, {i}] = {pulp.value(use[j, i])}")

    print("Total energy used:", pulp.value(prob.objective))

# Run the function
if __name__ == "__main__":
    schedule_deferable_demand()
