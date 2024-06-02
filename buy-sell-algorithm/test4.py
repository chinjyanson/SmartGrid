import numpy as np
import cvxpy as cp
import time
import data.server_data as data

def maximize_profit_mpc(initial_storage_level, max_storage_capacity, predicted_buy_prices, predicted_sell_prices, predicted_demand, time_step=1, horizon=15):

    initial_storage = initial_storage_level
    total_profit = 0
    n = len(predicted_buy_prices)

    for t in range(0, n-horizon, time_step):
        start_time = time.time()

        # Simulate real-time change
        energy_in = get_current_energy_in()
        energy_used = get_current_energy_used()
        current_buy_price, current_sell_price = get_current_buy_sell_prices()
        tick = get_tick()
        #start, end, energy = get_deferables()

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
            print(f"Tick: {tick}")
            print(f" energy_transactions.value: {energy_transactions.value}")
            print(f" storage_transactions.value: {storage_transactions.value}")
            print(f" solar_energy: {solar_energy.value}")
            print(f" demand: {demand.value}")
            print(f" storage: {storage_level.value}")
            print("Infeasible")
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
            print(f"Tick: {tick}")
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

# Example usage with mock functions for current energy
def get_current_energy_in():
    serve = data.server_data()
    serve.live_sunshine()
    area = 10
    sun_energy = serve.parsed_data['sun']
    solar_energy = sun_energy / area
    return solar_energy

def get_current_energy_used():
    serve = data.server_data()
    serve.live_demand()
    energy_demand = serve.parsed_data['demand']
    return energy_demand

def get_current_buy_sell_prices():
    serve = data.server_data()
    serve.live_prices()
    current_buy_price = serve.parsed_data['buy_price']
    current_sell_price = serve.parsed_data['sell_price']
    return current_buy_price, current_sell_price

def get_tick():
    serve = data.server_data()
    serve.get_ticks()
    tick = serve.parsed_data['tick']
    return tick

def get_deferables():
    serve = data.server_data()
    serve.deferables()
    start = serve.parsed_data['start']
    end = serve.parsed_data['end']
    energy = serve.parsed_data['energy']
    return start, end, energy


predicted_buy_prices = [0.97884838, 0.89573551, 0.75651526, 0.36626735, 0.09419675, 0.54257027, 
 0.68039317, 0.87333353, 0.19739547, 0.72302134, 0.67173916, 0.48412507, 
 0.64624241, 0.71897936, 0.98373854, 0.06747502, 0.31398806, 0.41772002, 
 0.75193036, 0.19930055, 0.160341  , 0.36658717, 0.09247076, 0.36090448, 
 0.62623211, 0.18597056, 0.04352059, 0.98483265, 0.27374228, 0.16594721, 
 0.07075692, 0.9261148 , 0.38126222, 0.61062392, 0.28653422, 0.705676  , 
 0.98333091, 0.35057567, 0.59573134, 0.40687669, 0.01086977, 0.11556685, 
 0.56960304, 0.91324145, 0.37973758, 0.99515715, 0.49952499, 0.4567768 , 
 0.06356873, 0.14114093, 0.25821279, 0.86992217, 0.31056673, 0.35155208, 
 0.67007042, 0.78291179, 0.84905628, 0.77026262, 0.01048405, 0.86917204]

predicted_sell_prices = [0.03194762, 0.45930612, 0.01051858, 0.69079694, 0.51206006,
 0.77535087, 0.10057117, 0.49460835, 0.91203877, 0.08952572,
 0.19057528, 0.01690927, 0.95617028, 0.30402571, 0.45785883,
 0.47598909, 0.84453514, 0.68161295, 0.14620774, 0.42293036,
 0.04753764, 0.63428545, 0.73821707, 0.28639252, 0.20461561,
 0.09949421, 0.01097188, 0.04416948, 0.96547974, 0.66680281,
 0.10233287, 0.27461902, 0.20731588, 0.49069655, 0.98324785,
 0.95886353, 0.02241813, 0.06577477, 0.27708673, 0.6320764 ,
 0.69405073, 0.77769733, 0.54160703, 0.32145207, 0.72802205,
 0.31492333, 0.20378386, 0.16166824, 0.67808081, 0.44890131,
 0.25668703, 0.43767515, 0.15153876, 0.62236015, 0.60261888,
 0.48828462, 0.96621227, 0.06060192, 0.44209771, 0.62306391]

predicted_demand = [0.68930846, 0.7082086 , 0.63636331, 0.5988409 , 0.30544195, 0.56052397, 
 0.68879429, 0.10792174, 0.17517828, 0.74036328, 0.15188816, 0.37261624, 
 0.87794606, 0.01026152, 0.76184164, 0.35642952, 0.70981649, 0.71206344, 
 0.15269325, 0.65844334, 0.9797104 , 0.63554534, 0.86394503, 0.17172609, 
 0.24588671, 0.83785965, 0.60799301, 0.1629502 , 0.0107552 , 0.89666861, 
 0.18507491, 0.60574117, 0.08043728, 0.23206797, 0.10741447, 0.9662969 , 
 0.31287944, 0.97211659, 0.62436168, 0.835991  , 0.85975781, 0.25064835, 
 0.98911537, 0.68811079, 0.68311063, 0.29208098, 0.40444325, 0.71085552, 
 0.40141714, 0.74311895, 0.07343258, 0.62053059, 0.10417085, 0.90518443, 
 0.18302153, 0.70323316, 0.33956219, 0.20709873, 0.08862838, 0.14611133]
initial_storage_level = 0
max_storage_capacity = 50

if __name__ == '__main__':
    max_profit = maximize_profit_mpc(initial_storage_level, max_storage_capacity, predicted_buy_prices, predicted_sell_prices, predicted_demand)
    print(f"Maximum Profit: {max_profit}")
