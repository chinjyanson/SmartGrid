import numpy as np
import cvxpy as cp
import time
import data.server_data as data
import predictions.train as train

def maximize_profit_mpc(initial_storage_level, max_storage_capacity, data_buffers, predictions_buffer, time_step=1, horizon=10):

    #print(predictions_buffer)
    predicted_buy_prices = predictions_buffer['buy_price']
    predicted_sell_prices = predictions_buffer['sell_price']
    predicted_demand = predictions_buffer['demand']

    initial_storage = initial_storage_level
    total_profit = 0
    #n = len(predicted_buy_prices)
    n = 60


    for t in range(0, n-horizon, time_step):
        start_time = time.time()

        #print(data_buffers)
        # Simulate real-time change
        energy_in = data_buffers['sun'][-1]
        energy_used = data_buffers['demand'][-1]
        current_buy_price = data_buffers['buy_price'][-1]
        current_sell_price = data_buffers['sell_price'][-1]
        energy_in = energy_in * 0.1 # Convert from Wh to kWh
        #start, end, energy = get_deferables()
        serve = data.server_data()
        serve.deferables()
        deferables = serve.parsed_data['deferables']
        print(deferables)

        print(f"  Get Energy In: {energy_in} kWh")
        print(f"  Get Energy Used: {energy_used} kWh")
        print(f"  Get Buy Price: {current_buy_price} £/kWh")
        print(f"  Get Sell Price: {current_sell_price} £/kWh")

        if t == 0:
            storage = initial_storage
        else:
            storage = storage

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

        # Objective function
        profit = cp.sum(cp.multiply(neg_energy_transactions, predicted_sell_prices[t:t + horizon]) - cp.multiply(pos_energy_transactions, predicted_buy_prices[t:t + horizon]))

        # Constraints
        constraints = [
            storage_level[0] == storage,  # storage level currently
            solar_energy[0] == energy_in,
            demand[0] == energy_used,
            energy_transactions == pos_energy_transactions - neg_energy_transactions,
            storage_transactions == pos_storage_transactions - neg_storage_transactions,
            pos_energy_transactions + solar_energy - demand - neg_energy_transactions >= 0,
            energy_transactions + storage_transactions + solar_energy - demand >= 0,
            solar_energy[0] - demand[0] <= -energy_transactions[0] - storage_transactions[0], 
        ]

        for i in range(horizon):
            constraints += [
                storage_level[i + 1] == storage_level[i] - storage_transactions[i],
                storage_level[i + 1] <= max_storage_capacity,
                storage_level[i + 1] >= 0,
                neg_energy_transactions[i] <= storage_level[i], # Can only sell if we have enough in the storage
                pos_energy_transactions[i] <= max_storage_capacity - storage_level[i],  # Can only buy if we have enough storage capacity
            ]
        
        for i in range(1, horizon):  # Starting from 1 since solar_energy[0] is fixed to energy_in
            constraints += [
                solar_energy[i] == 0,  # Worst-case scenario
                demand[i] == predicted_demand[i],  # Predicted demand
                #storage_level[i] == storage_level[i-1] - storage_transactions[i-1],
            ]

        # Define problem
        problem = cp.Problem(cp.Maximize(profit), constraints)

        # Solve problem
        problem.solve(solver=cp.CBC)  # Using CBC mixed-integer solver (Coin-or branch and cut)

        if problem.status == cp.INFEASIBLE:
            print(f"Cycle {t//time_step + 1}:")
            #print(f"Tick: {tick}")
            print(f" energy_transactions.value: {energy_transactions.value}")
            print(f" storage_transactions.value: {storage_transactions.value}")
            print(f" solar_energy: {solar_energy.value}")
            print(f" demand: {demand.value}")
            print(f" storage: {storage_level.value}")
            print("Infeasible")

            #use naive solution if solution is infeasible
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
                if storage + energy_in <= max_storage_capacity:
                    storage += energy_in
                else:
                    excess_energy = storage + energy_in - max_storage_capacity
                    total_profit += excess_energy * current_sell_price
                    storage = max_storage_capacity
            
        elif problem.status == cp.OPTIMAL or problem.status == cp.FEASIBLE:
            optimal_energy_transaction = energy_transactions.value[0]   
            optimal_storage_transaction = storage_transactions.value[0]

            # Update storage and profit based on actual prices
            if optimal_energy_transaction < 0:  
                total_profit -= optimal_energy_transaction * current_sell_price 
            elif optimal_energy_transaction > 0:
                total_profit -= optimal_energy_transaction * current_buy_price

            # Ensure storage is within bounds after transactions
            storage -= optimal_storage_transaction
            storage = min(max(storage, 0), max_storage_capacity)

            print(f"Cycle {t//time_step + 1}:")
            #print(f"Tick: {tick}")
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

            #storage -= optimal_storage_transaction 
        else:
            print(f"Cycle {t//time_step + 1}: Optimization failed")
            print(problem.status)

        # Factor in the code time taken into the sleep time (call every 5 seconds regardless of code)
        end_time = time.time()
        execution_time = end_time - start_time
        print(execution_time)
        sleep_time = max(0, 5 - execution_time)
        time.sleep(sleep_time)

    return total_profit



if __name__ == '__main__':
    print("Running optimization")
    #  while True:
    #         if(i == 0):
    #             cycle_count += 1

    #             print("Cycle ", cycle_count)
    #             print()

    #             time_taken = new_cycle(data_buffers, predictions, next_predictions)

    #         elif((i % 15) == 0 or (i == 59)):
    #             time_taken, next_predictions, data_buffers = prepare_next(i, starting_i, data_buffers, next_predictions)

    #             print("Preparation took ", time_taken)
            
    #         else:
    #             # trainer has not been called yet at this point => server didn't start at 0
    #             # need to set predictions to be entire previous cycle
    #             time_taken = something_else(data_buffers, predictions)
    #             print("Something else took ", time_taken)
 
    #         if(5-time_taken < 0):
    #             print("Something took too much time ", time_taken)
    #             sys.exit(1)
    #         else:
    #             time.sleep(5-time_taken)
    #             i = (i + 1) % 60           
    #         print("Current tick ", i)

    # main()

    # max_profit = maximize_profit_mpc(initial_storage_level, max_storage_capacity, data_buffers)
    # print(f"Maximum Profit: {max_profit}")